from enum import Enum

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


class PaymentType(Enum):
    Differentiated = 1
    Annuity = 2


class Credit:
    def __init__(self, loan_sum: int, loan_period: int, percentage_rate: int, payment_type: PaymentType):
        self._loan_sum = loan_sum  # сумма кредита
        self._loan_period = loan_period  # период кредитования
        self._percentage_rate = percentage_rate  # процентная ставка (годовая)
        self._payment_type = payment_type  # тип платежа
        self._payment_sum = []  # сумма платежа
        self._principal_credit = []  # основной долг
        self._percentages = []  # проценты
        self._remaining_credit = []  # остаток долга

    @property
    def loan_sum(self):
        return self._loan_sum

    @property
    def loan_period(self):
        return self._loan_period

    @property
    def percentage_rate(self):
        return self._percentage_rate

    @property
    def payment_type(self):
        return self._payment_type

    @property
    def payment_sum(self):
        return self._payment_sum

    @property
    def principal_credit(self):
        return self._principal_credit

    @property
    def percentages(self):
        return self._percentages

    @property
    def remaining_credit(self):
        return self._remaining_credit

    def calculate_payments(self):
        if self._payment_type is PaymentType.Differentiated:
            self.calculate_differentiated()
        else:
            self.calculate_annuity()

    def calculate_differentiated(self):
        percentages = self._percentage_rate / 1200
        for n in range(self._loan_period, 0, -1):
            principal_credit = self._loan_sum / self._loan_period
            self._principal_credit.append(round(principal_credit, 2))

            current_percentages = principal_credit * n * percentages
            self._percentages.append(round(current_percentages, 2))

            payment_sum = principal_credit + current_percentages
            self._payment_sum.append(round(payment_sum))

            if len(self._remaining_credit) == 0:
                self._remaining_credit.append(round(self._loan_sum - principal_credit, 2))
            else:
                remaining_credit = self._remaining_credit[len(self._remaining_credit) - 1] - principal_credit
                self._remaining_credit.append(round(remaining_credit, 2))

    def calculate_annuity(self):
        percentages = self._percentage_rate / 1200
        for n in range(self._loan_period, 0, -1):
            payment_sum = self._loan_sum * percentages * (percentages + 1) ** self._loan_period / \
                          ((percentages + 1) ** self._loan_period - 1)
            self._payment_sum.append(round(payment_sum, 2))

            if len(self._remaining_credit) == 0:
                remains = self._loan_sum
            else:
                remains = self._remaining_credit[len(self._remaining_credit) - 1]
            current_percentages = remains * percentages
            self._percentages.append(round(current_percentages, 2))

            principal_credit = payment_sum - current_percentages
            self._principal_credit.append(round(principal_credit, 2))

            remaining_credit = remains - principal_credit
            self._remaining_credit.append(round(remaining_credit, 2))

    def create_payments(self):
        payments = []
        for n in range(0, self._loan_period):
            payment = Payment(n + 1, self._payment_sum[n], self._principal_credit[n],
                              self._percentages[n], self._remaining_credit[n])
            payments.append(payment)
        return payments

    def calculate_overpayment(self):
        overpayment = 0
        for percent in self._percentages:
            overpayment = overpayment + percent
        return overpayment


class Payment():
    def __init__(self, payment_number, payment_sum, principal_credit, percentages, remaining_credit):
        self.payment_number = payment_number
        self.payment_sum = payment_sum
        self.principal_credit = principal_credit
        self.percentages = percentages
        self.remaining_credit = remaining_credit


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        loan_sum = int(request.form.get('loan_sum'))
        loan_period = int(request.form.get('loan_period'))
        percentage_rate = int(request.form.get('percentage_rate'))
        payment_type_str = request.form.get('payment_type')
        if payment_type_str == 'Annuity':
            payment_type = PaymentType.Annuity
            payment_type_str = 'Аннуительный'
        else:
            payment_type = PaymentType.Differentiated
            payment_type_str = 'Дифференцированный'

        credit = Credit(loan_sum, loan_period, percentage_rate, payment_type)
        credit.calculate_payments()
        payments = credit.create_payments()
        overpayment = credit.calculate_overpayment()

        return render_template('result_page.html', title='График платежей',
                               payments=payments, overpayment=round(overpayment, 2), loan_sum=loan_sum,
                               loan_period=loan_period, percentage_rate=percentage_rate, payment_type=payment_type_str)


@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == 'GET':
        return render_template('index.html')


if __name__ == '__main__':
    app.run()
