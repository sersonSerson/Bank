from collections import deque


class Calculator:

    operations = {'+': {'Description': 'Add', 'Priority': 1, 'Stacked': True, 'Symbol': '+'},
                  '-': {'Description': 'Subtract', 'Priority': 1, 'Stacked': True, 'Symbol': '-'},
                  '*': {'Description': 'Multiply', 'Priority': 2, 'Stacked': False, 'Symbol': '*'},
                  '/': {'Description': 'Divide', 'Priority': 2, 'Stacked': False, 'Symbol': '/'},
                  '(': {'Description': 'Left Parentheses', 'Priority': 0, 'Stacked': False, 'Symbol': '('},
                  ')': {'Description': 'Right Parentheses', 'Priority': 0, 'Stacked': False, 'Symbol': ')'}}
    variables = dict()

    def __init__(self):
        self.calculating = True
        # self.get_input()

    def get_input(self):
        user = input()
        # user = '8 * 3 + 12 * (4 - 2)'
        # user = '33 + 20 + 11 + 49 - 32 - 9 + 1 - 80 + 4'
        # print(user)
        # user = '8 3 12 4 2'
        if not user:
            return

        if user.startswith('/'):
            self.command(user)
        elif '=' in user:
            self.assign(user)
        else:
            self.calculate(user)

    def command(self, command):

        if command == '/help':
            print('The program calculates the sum, the difference or any other ariphmetic operations with '
                  'numbers with assignments')
        elif command == '/exit':
            print('Bye!')
            self.calculating = False
        else:
            print('Unknown command')

    def assign(self, user):
        variable_name, variable_value = self.variable_parameters(user)
        if self.valid_identifier(variable_name):
            if self.is_digit(variable_value):
                variable_value = int(variable_value)

            elif self.valid_identifier(variable_value):
                if self.is_variable(variable_value):
                    variable_value = int(self.fetch_variable(variable_value))
                else:
                    variable_value = 0
                    print('Unknown variable')
            Calculator.variables[variable_name] = variable_value

    def calculate(self, user):

        result = ''
        error = False
        continued = False
        my_stack = deque()
        current = ''
        if '**' in user or '//' in user:
            print('Invalid expression')
            return

        for i in user:
            if i == ' ':
                continued = False
                continue
            elif self.is_action(i):
                if current:
                    error = True
                    print('Unknown variable')
                result, my_stack, error = self.add_operator(my_stack, result, self.choose_action(i), error)
                continued = False
            elif self.is_digit(i):
                if current:
                    error = True
                    print('Unknown variable')
                result = self.add_digit(i, result, continued)
                continued = True
            elif not self.valid_identifier(current + i):
                error = True
            elif self.is_variable(current + i):
                result = self.add_digit(self.fetch_variable(current + i), result,  continued)
                continued = False
                current = ''
            else:
                continued = True
                current += i

            if current:
                error = True
                print('Unknown variable')
            elif error:
                error = True
                print('Invalid expression')
                break

        if not error and result != '':
            for i in range(len(my_stack)):
                stacked_action = my_stack.pop()
                if stacked_action['Symbol'] in ['(', ')']:
                    error = True
                    print('Invalid expression')
                    break
                result += ' ' + stacked_action['Symbol']
            # print(result)
            result = self.make_action(result)

        if not error:
            print(result)

    def add_digit(self, i, result, continued):
        value = int(i)
        if continued or result == '':
            result += str(value)
        else:
            result += ' ' + str(value)
        return result

    def add_operator(self, my_stack, result, action, error):

        last_action_priority = 0
        priority = action['Priority']
        symbol = action['Symbol']

        if len(my_stack) > 0:
            last_action_priority = my_stack[len(my_stack)-1]['Priority']
        if symbol == '(':
            my_stack.append(action)
        elif symbol == ')':
            found_parenthesis = False
            while len(my_stack) > 0:
                stacked_action = my_stack.pop()
                if stacked_action['Symbol'] == '(':
                    found_parenthesis = True
                    break

                if stacked_action['Symbol'] in ['(', ')']:
                    continue
                result += ' ' + stacked_action['Symbol']
            if not found_parenthesis:
                error = True
        elif priority > last_action_priority:
            my_stack.append(action)
        else:
            while len(my_stack) > 0 and priority <= my_stack[0]['Priority']:
                stacked_action = my_stack.pop()
                if stacked_action['Symbol'] in ['(', ')']:
                    continue
                result += ' ' + stacked_action['Symbol']
            my_stack.append(action)
        return result, my_stack, error

    def make_action(self, result):
        calculation_stack = deque()

        try:
            for i in result.split():
                if self.is_action(i):
                    first_number = int(calculation_stack.pop())
                    second_number = int(calculation_stack.pop())
                    if i == '+':
                        calculation_result = self.addition(first_number, second_number)
                    elif i == '-':
                        calculation_result = self.subtraction(second_number, first_number)
                    elif i == '*':
                        calculation_result = self.multiplication(first_number, second_number)
                    elif i == '/':
                        calculation_result = self.division(second_number, first_number)
                    calculation_stack.append(calculation_result)

                    # action = Calculator.operations[i]
                    # action['Description']
                elif self.is_digit(i):
                    calculation_stack.append(int(i))
                else:
                    raise ValueError
            return calculation_stack.pop()
        except ValueError:
            result = 'Invalid expression'
        # return result

    @staticmethod
    def variable_parameters(user):
        variable_parameters = user.split('=')
        return variable_parameters[0].strip(), variable_parameters[1].strip()

    @staticmethod
    def valid_identifier(variable_name):

        valid = True
        for i in list('1234567890'):
            if i in variable_name:
                valid = False
                print('Invalid identifier')

        return valid

    @staticmethod
    def fetch_variable(name):
        return Calculator.variables[name]

    @staticmethod
    def is_variable(name):
        if name in Calculator.variables:
            return True
        else:
            # print('Unknown variable')
            return False

    @staticmethod
    def is_action(name):

        is_action = False
        if name[0] in Calculator.operations:
            action = Calculator.operations[name[0]]
            if (len(name) > 1 and action['Stacked']) or len(name) == 1:
                is_action = True

        return is_action

    @staticmethod
    def is_digit(name):
        return name.replace('-', '').isdigit()

    @staticmethod
    def choose_action(user):

        action = Calculator.operations[user[0]]
        if user == '-' * len(user):
            if len(user) % 2 == 0:
                Calculator.operations['+']

        return action

    @staticmethod
    def addition(result, value):
        result += int(value)
        return result

    @staticmethod
    def subtraction(result, value):
        result -= int(value)

        return result

    @staticmethod
    def multiplication(result, value):
        result *= int(value)

        return result

    @staticmethod
    def division(result, value):
        result /= int(value)

        return result


calc = Calculator()
while calc.calculating:
    calc.get_input()
    # calc.calculating = False
