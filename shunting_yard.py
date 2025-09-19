from manim import *
import re


class ShuntingYardVisualization(Scene):
    def construct(self):
        # change this shit for shitshow to happen :D
        expression = "10 - 4 / 3 + 4^(2 - 0.5)"

        self.visualize_shunting_yard(expression)

    def format_number(self, num):
        if num == int(num):
            return f"{int(num)}"
        else:
            return f"{round(num, 2)}"

    def visualize_shunting_yard(self, expression):
        title = Text("Shunting Yard Algorithm", font_size=48, color=BLUE).to_edge(UP)
        self.play(Write(title))

        tokens = self.tokenize(expression)

        expr_label = Text("Expression: ", font_size=36)
        self.expression_parts = VGroup(*[Text(token, font_size=36) for token in tokens])
        self.expression_parts.arrange(RIGHT, buff=0.15)
        self.full_expression_display = VGroup(
            expr_label, self.expression_parts
        ).arrange(RIGHT, buff=0.1)
        self.full_expression_display.next_to(title, DOWN, buff=0.5)
        self.play(Write(self.full_expression_display))

        self.create_visual_elements()
        self.wait(1)

        output_queue = []
        operator_stack = []
        self.highlight_box = None

        for i, token in enumerate(tokens):
            self.highlight_current_token_in_line(i)
            current_token_mobj = self.expression_parts[i]

            if self.is_number(token):
                self.process_number(token, output_queue, current_token_mobj)
            elif self.is_operator(token):
                self.process_operator(
                    token, output_queue, operator_stack, current_token_mobj
                )
            elif token == "(":
                self.process_left_paren(token, operator_stack, current_token_mobj)
            elif token == ")":
                self.process_right_paren(output_queue, operator_stack)

            self.wait(0.8)

        if self.highlight_box:
            self.play(FadeOut(self.highlight_box))

        self.pop_remaining_operators(output_queue, operator_stack)

        self.show_final_result(output_queue)
        self.wait(2)
        self.evaluate_postfix(output_queue)

    # if i dont fix this in a week im gay
    def create_visual_elements(self):
        vertical_center = -1.5
        margin = 0.7

        self.output_label = (
            Text("Output Queue:", font_size=24, color=GREEN)
            .to_edge(LEFT)
            .set_y(vertical_center + margin)
        )
        self.stack_label = (
            Text("Operator Stack:", font_size=24, color=RED)
            .to_edge(LEFT)
            .set_y(vertical_center - margin)
        )

        box_width = 8
        box_height = 1
        box_x_position = 2.5

        # fuck you lsp. >:(
        self.output_box = Rectangle(
            width=box_width, height=box_height, color=GREEN
        ).move_to([box_x_position, vertical_center + margin, 0])
        self.stack_box = Rectangle(
            width=box_width, height=box_height, color=RED
        ).move_to([box_x_position, vertical_center - margin, 0])

        self.play(
            Write(self.output_label),
            Write(self.stack_label),
            Create(self.output_box),
            Create(self.stack_box),
        )

        self.output_group = VGroup().move_to(self.output_box.get_center())
        self.stack_group = VGroup().move_to(self.stack_box.get_center())
        self.add(self.output_group, self.stack_group)

    def tokenize(self, expression):
        return [
            token
            for token in re.findall(r"(\d*\.?\d+|[+\-*/^()])", expression)
            if not token.isspace()
        ]

    def is_number(self, token):
        try:
            float(token)
            return True
        except ValueError:
            return False

    def is_operator(self, token):
        return token in ["+", "-", "*", "/", "^"]

    def get_precedence(self, op):
        return {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}.get(op, 0)

    def is_right_associative(self, op):
        return op == "^"

    def _show_subtitle(self, text, size=24, position_relative_to=None):
        if position_relative_to is None:
            position_relative_to = self.full_expression_display
        explanation = Text(text, font_size=size, color=WHITE).next_to(
            position_relative_to, DOWN, buff=0.4
        )
        self.play(Write(explanation))
        self.wait(0.8)
        self.play(FadeOut(explanation))

    def highlight_current_token_in_line(self, token_index):
        animations = []
        if self.highlight_box:
            animations.append(FadeOut(self.highlight_box))
        token_to_highlight = self.expression_parts[token_index]
        self.highlight_box = SurroundingRectangle(
            token_to_highlight,
            color=YELLOW,
            fill_color=YELLOW,
            fill_opacity=0.3,
            buff=0.1,
        )
        animations.append(Create(self.highlight_box))
        self.play(*animations, run_time=0.4)

    def process_number(self, token, output_queue, token_mobj):
        self._show_subtitle(f"Number '{token}' → Output Queue")
        output_queue.append(token)

        new_mobj = token_mobj.copy().set_color(GREEN)
        self.output_group.add(new_mobj)

        self.play(
            self.output_group.animate.arrange(RIGHT, buff=0.5).move_to(
                self.output_box.get_center()
            )
        )

    def process_operator(self, token, output_queue, operator_stack, token_mobj):
        animations = []
        while (
            operator_stack
            and operator_stack[-1] != "("
            and (
                self.get_precedence(operator_stack[-1]) > self.get_precedence(token)
                or (
                    self.get_precedence(operator_stack[-1])
                    == self.get_precedence(token)
                    and not self.is_right_associative(token)
                )
            )
        ):

            self._show_subtitle(f"Pop '{operator_stack[-1]}' to output", size=20)
            op = operator_stack.pop()
            output_queue.append(op)

            op_mobj = self.stack_group[-1]
            op_mobj.set_color(GREEN)
            self.stack_group.remove(op_mobj)
            self.output_group.add(op_mobj)

            self.play(
                self.stack_group.animate.arrange(RIGHT, buff=0.5).move_to(
                    self.stack_box.get_center()
                ),
                self.output_group.animate.arrange(RIGHT, buff=0.5).move_to(
                    self.output_box.get_center()
                ),
            )

        self._show_subtitle(f"Operator '{token}' → Push to stack", size=20)
        operator_stack.append(token)
        new_mobj = token_mobj.copy().set_color(RED)
        self.stack_group.add(new_mobj)
        self.play(
            self.stack_group.animate.arrange(RIGHT, buff=0.5).move_to(
                self.stack_box.get_center()
            )
        )

    def process_left_paren(self, token, operator_stack, token_mobj):
        self._show_subtitle("Left parenthesis → Push to stack")
        operator_stack.append(token)
        new_mobj = token_mobj.copy().set_color(RED)
        self.stack_group.add(new_mobj)
        self.play(
            self.stack_group.animate.arrange(RIGHT, buff=0.5).move_to(
                self.stack_box.get_center()
            )
        )

    def process_right_paren(self, output_queue, operator_stack):
        self._show_subtitle("Right parenthesis → Pop until '('")

        while operator_stack and operator_stack[-1] != "(":
            op = operator_stack.pop()
            output_queue.append(op)

            op_mobj = self.stack_group[-1]
            op_mobj.set_color(GREEN)
            self.stack_group.remove(op_mobj)
            self.output_group.add(op_mobj)

            self.play(
                self.stack_group.animate.arrange(RIGHT, buff=0.5).move_to(
                    self.stack_box.get_center()
                ),
                self.output_group.animate.arrange(RIGHT, buff=0.5).move_to(
                    self.output_box.get_center()
                ),
                run_time=0.5,
            )

        if operator_stack and operator_stack[-1] == "(":
            operator_stack.pop()
            paren_mobj = self.stack_group[-1]
            self.stack_group.remove(paren_mobj)

            self.play(
                FadeOut(paren_mobj),
                self.stack_group.animate.arrange(RIGHT, buff=0.5).move_to(
                    self.stack_box.get_center()
                ),
                run_time=0.5,
            )

    def pop_remaining_operators(self, output_queue, operator_stack):
        while operator_stack:
            self._show_subtitle(f"Pop remaining '{operator_stack[-1]}' to output")
            op = operator_stack.pop()
            output_queue.append(op)

            op_mobj = self.stack_group[-1]
            op_mobj.set_color(GREEN)
            self.stack_group.remove(op_mobj)
            self.output_group.add(op_mobj)

            self.play(
                self.stack_group.animate.arrange(RIGHT, buff=0.5).move_to(
                    self.stack_box.get_center()
                ),
                self.output_group.animate.arrange(RIGHT, buff=0.5).move_to(
                    self.output_box.get_center()
                ),
            )
            self.wait(0.5)

    def show_final_result(self, output_queue):
        final_label = Text("Final Postfix Expression: ", font_size=28, color=GREEN)
        final_expr_text = Text(f"{' '.join(output_queue)}", font_size=28, color=WHITE)
        final_group = VGroup(final_label, final_expr_text).arrange(RIGHT)
        final_group.next_to(self.full_expression_display, DOWN, buff=0.5)
        final_box = SurroundingRectangle(final_group, color=GREEN, buff=0.2)

        self.play(Write(final_group))
        self.play(Create(final_box))
        self.wait(1)

    def evaluate_postfix(self, postfix_tokens):
        self.clear()
        eval_title = Text(
            "Evaluating Postfix Expression", font_size=36, color=PURPLE
        ).to_edge(UP)
        self.play(Write(eval_title))

        postfix_label = Text("Postfix: ", font_size=28)
        self.postfix_parts = VGroup(
            *[Text(token, font_size=28) for token in postfix_tokens]
        ).arrange(RIGHT, buff=0.2)
        self.full_postfix_display = (
            VGroup(postfix_label, self.postfix_parts)
            .arrange(RIGHT, buff=0.1)
            .next_to(eval_title, DOWN, buff=0.5)
        )
        self.play(Write(self.full_postfix_display))

        vertical_center = -1.5
        margin = 0.7
        eval_stack_label = (
            Text("Evaluation Stack:", font_size=24, color=PURPLE)
            .to_edge(LEFT)
            .set_y(vertical_center + margin)
        )
        operation_label = (
            Text("Operation:", font_size=24, color=YELLOW)
            .to_edge(LEFT)
            .set_y(vertical_center - margin)
        )

        box_x_position = 2.5
        eval_stack_box = Rectangle(width=8, height=1, color=PURPLE).move_to(
            [box_x_position, vertical_center + margin, 0]
        )
        operation_box = Rectangle(width=8, height=1, color=YELLOW).move_to(
            [box_x_position, vertical_center - margin, 0]
        )

        self.play(
            Write(eval_stack_label),
            Write(operation_label),
            Create(eval_stack_box),
            Create(operation_box),
        )

        operation_display = Text("", font_size=20, color=YELLOW).move_to(
            operation_box.get_center()
        )
        self.eval_stack_group = VGroup().move_to(eval_stack_box.get_center())
        self.add(operation_display, self.eval_stack_group)

        eval_stack = []
        self.eval_highlight_box = None

        for i, token in enumerate(postfix_tokens):
            self.highlight_current_postfix_token(i)
            self.wait(0.5)

            if self.is_number(token):
                self._show_subtitle(
                    f"Number '{token}' → Push to stack",
                    position_relative_to=self.full_postfix_display,
                    size=24,
                )

                eval_stack.append(float(token))
                new_num_mobj = Text(token, font_size=28, color=PURPLE)
                self.eval_stack_group.add(new_num_mobj)
                self.play(
                    self.eval_stack_group.animate.arrange(RIGHT, buff=0.5).move_to(
                        eval_stack_box.get_center()
                    )
                )

                new_op_disp = Text("", font_size=20, color=YELLOW).move_to(
                    operation_box.get_center()
                )
                self.play(Transform(operation_display, new_op_disp), run_time=0.25)
            else:
                if len(eval_stack) >= 2:
                    b_val = eval_stack.pop()
                    a_val = eval_stack.pop()
                    result = self.apply_operator(a_val, b_val, token)
                    eval_stack.append(result)

                    # shit so long doesn't fit on screen :D
                    op_string = f"{self.format_number(a_val)} {token} {self.format_number(b_val)} = {self.format_number(result)}"
                    new_op_disp = Text(op_string, font_size=20, color=YELLOW).move_to(
                        operation_box.get_center()
                    )
                    self.play(Transform(operation_display, new_op_disp))

                    b_mobj = self.eval_stack_group[-1]
                    a_mobj = self.eval_stack_group[-2]
                    self.eval_stack_group.remove(a_mobj, b_mobj)

                    result_mobj = Text(
                        self.format_number(result), font_size=28, color=PURPLE
                    )
                    self.eval_stack_group.add(result_mobj)

                    self.play(
                        FadeOut(a_mobj, b_mobj),
                        self.eval_stack_group.animate.arrange(RIGHT, buff=0.5).move_to(
                            eval_stack_box.get_center()
                        ),
                    )
            self.wait(0.5)

        if self.eval_highlight_box:
            self.play(FadeOut(self.eval_highlight_box))

        result_val = self.format_number(eval_stack[0]) if eval_stack else "Error"
        final_result_text = Text(
            f"Final Result: {result_val}", font_size=32, color=GOLD
        )
        final_result_text.next_to(self.full_postfix_display, DOWN, buff=0.5)
        final_result_box = SurroundingRectangle(final_result_text, color=GOLD, buff=0.2)

        self.play(Write(final_result_text))
        self.play(Create(final_result_box))
        self.wait(3)

    def highlight_current_postfix_token(self, token_index):
        animations = []
        if self.eval_highlight_box:
            animations.append(FadeOut(self.eval_highlight_box))
        token_to_highlight = self.postfix_parts[token_index]
        self.eval_highlight_box = SurroundingRectangle(
            token_to_highlight,
            color=ORANGE,
            fill_color=ORANGE,
            fill_opacity=0.3,
            buff=0.1,
        )
        animations.append(Create(self.eval_highlight_box))
        self.play(*animations, run_time=0.4)

    def apply_operator(self, a, b, op):
        if op == "+":
            return a + b
        elif op == "-":
            return a - b
        elif op == "*":
            return a * b
        elif op == "/":
            return a / b if b != 0 else float("inf")
        elif op == "^":
            return a**b
        return 0


# class ShuntingYardExample2(ShuntingYardVisualization):
#     def construct(self):
#         expression = "5 * ( 3 + 2 ) - 8 / 4.5"
#         self.visualize_shunting_yard(expression)
