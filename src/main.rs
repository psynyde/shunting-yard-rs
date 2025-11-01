use std::collections::VecDeque;
use std::env;

#[derive(Debug, Clone)]
enum Type {
    Number(f32),
    Operator(char),
    LParen,
    RParen,
}

#[derive(Debug, Clone)]
struct Token {
    typ: Type,
    precedence: u8,
}

impl Token {
    fn new(typ: Type) -> Self {
        let precedence = match &typ {
            Type::Number(_) => 0,
            Type::Operator(op) => match op {
                '+' | '-' => 1,
                '*' | '/' => 2,
                '^' => 3,
                _ => 0,
            },
            Type::LParen | Type::RParen => 0,
        };
        Token { typ, precedence }
    }
}

fn tokenize(input: &str) -> Result<VecDeque<Token>, String> {
    let mut tokens = VecDeque::new();
    let mut chars = input.chars().peekable();

    while let Some(ch) = chars.next() {
        match ch {
            ' ' => continue,
            '+' | '-' | '*' | '/' | '^' => {
                tokens.push_back(Token::new(Type::Operator(ch)));
            }
            '(' => tokens.push_back(Token::new(Type::LParen)),
            ')' => tokens.push_back(Token::new(Type::RParen)),
            '0'..='9' | '.' => {
                let mut number_str = String::new();
                number_str.push(ch);

                while let Some(&next_ch) = chars.peek() {
                    if next_ch.is_ascii_digit() || next_ch == '.' {
                        number_str.push(chars.next().unwrap());
                    } else {
                        break;
                    }
                }

                match number_str.parse::<f32>() {
                    Ok(num) => tokens.push_back(Token::new(Type::Number(num))),
                    Err(_) => return Err(format!("Invalid number: {}", number_str)),
                }
            }
            _ => return Err(format!("Unknown character: {}", ch)),
        }
    }

    Ok(tokens)
}

fn print_tokens(tokens: &VecDeque<Token>) {
    for (i, token) in tokens.iter().enumerate() {
        match &token.typ {
            Type::Number(n) => {
                println!("  {}: Number({}) [precedence: {}]", i, n, token.precedence)
            }
            Type::Operator(op) => println!(
                "  {}: Operator('{}') [precedence: {}]",
                i, op, token.precedence
            ),
            Type::LParen => println!("  {}: LeftParen [precedence: {}]", i, token.precedence),
            Type::RParen => println!("  {}: RightParen [precedence: {}]", i, token.precedence),
        }
    }
}

fn shunting_yard(tokens: &VecDeque<Token>) -> Result<VecDeque<Token>, String> {
    let mut output_queue = VecDeque::new();
    let mut operator_stack: Vec<Token> = Vec::new();

    for token in tokens {
        match token.typ {
            Type::Number(_) => output_queue.push_back(token.clone()),
            Type::Operator(op) => {
                while let Some(top_op_token) = operator_stack.last() {
                    if let Type::Operator(_top_op) = top_op_token.typ {
                        let is_left_associative = op != '^';
                        if (is_left_associative && token.precedence <= top_op_token.precedence)
                            || (!is_left_associative && token.precedence < top_op_token.precedence)
                        {
                            output_queue.push_back(operator_stack.pop().unwrap());
                        } else {
                            break;
                        }
                    } else {
                        break;
                    }
                }
                operator_stack.push(token.clone());
            }
            Type::LParen => operator_stack.push(token.clone()),
            Type::RParen => {
                let mut found_lparen = false;
                while let Some(top_op_token) = operator_stack.last() {
                    if let Type::LParen = top_op_token.typ {
                        found_lparen = true;
                        break;
                    }
                    output_queue.push_back(operator_stack.pop().unwrap());
                }

                if found_lparen {
                    operator_stack.pop(); // Discard the LParen
                } else {
                    return Err("Mismatched parentheses".to_string());
                }
            }
        }
    }

    while let Some(op_token) = operator_stack.pop() {
        if let Type::LParen | Type::RParen = op_token.typ {
            return Err("Mismatched parentheses".to_string());
        }
        output_queue.push_back(op_token);
    }

    Ok(output_queue)
}

fn evaluate_rpn(rpn_queue: &VecDeque<Token>) -> Result<f32, String> {
    let mut value_stack = Vec::new();

    for token in rpn_queue {
        match token.typ {
            Type::Number(n) => value_stack.push(n),
            Type::Operator(op) => {
                if value_stack.len() < 2 {
                    return Err(format!(
                        "Invalid RPN expression: operator {} requires two operands",
                        op
                    ));
                }
                let b = value_stack.pop().unwrap();
                let a = value_stack.pop().unwrap();

                let result = match op {
                    '+' => a + b,
                    '-' => a - b,
                    '*' => a * b,
                    '/' => a / b,
                    '^' => a.powf(b),
                    _ => return Err(format!("Unknown operator: {}", op)),
                };
                value_stack.push(result);
            }
            _ => return Err("Invalid token in RPN queue".to_string()),
        }
    }

    if value_stack.len() == 1 {
        Ok(value_stack[0])
    } else {
        Err("Invalid RPN expression: stack should have one value at the end".to_string())
    }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();

    if args.is_empty() {
        eprintln!("Please provide an expression as a command-line argument.");
        eprintln!("Usage: shunting-yard-rs \"3 + 4 * 2 / ( 1 - 5 ) ^ 2\"");
        eprintln!("Note: On some shells, you may need to escape characters like '*' or '()'.");
        return;
    }

    let input = args.join(" ");
    println!("Input: {}", input);

    match tokenize(&input) {
        Ok(tokens) => {
            println!("\nParsed tokens:");
            print_tokens(&tokens);
            match shunting_yard(&tokens) {
                Ok(rpn_queue) => {
                    println!( "\n RPN (postfix) expression:");
                    print_tokens(&rpn_queue);
                    match evaluate_rpn(&rpn_queue) {
                        Ok(result) => println!("\n Result: {}", result),
                        Err(e) => eprintln!("Error evaluating RPN: {}", e),
                    }
                }
                Err(e) => eprintln!("Error in shunting yard: {}", e),
            }
        }
        Err(e) => {
            eprintln!("Error parsing input: {}", e);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_expression() {
        let tokens = tokenize("2 /3 ^ 4").unwrap();
        assert_eq!(tokens.len(), 5);

        match &tokens[0].typ {
            Type::Number(n) => assert_eq!(*n, 2.0),
            _ => panic!("Expected number"),
        }
    }

    #[test]
    fn test_decimal_numbers() {
        let tokens = tokenize("3.14 + 2.5").unwrap();
        match &tokens[0].typ {
            Type::Number(n) => assert_eq!(*n, 3.14),
            _ => panic!("Expected number"),
        }
    }

    #[test]
    fn test_complex_expression() {
        let tokens = tokenize("10- 4 / 3 + 4^(2 - 0.5)").unwrap();
        assert_eq!(tokens.len(), 13);
    }

    #[test]
    fn test_evaluation() {
        let tokens = tokenize("3 + 4 * 2 / ( 1 - 5 ) ^ 2").unwrap();
        let rpn = shunting_yard(&tokens).unwrap();
        let result = evaluate_rpn(&rpn).unwrap();
        assert_eq!(result, 3.5);
    }
}
