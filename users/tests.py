from django.test import TestCase
from users.forms import UserRegistrationForm, AccountRegistrationForm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# General registration form testing
class UserRegistrationFormTest(TestCase):
    # Test for no input into the form.
    # Output: Not a valid form
    def test_empty_form(self):
        registrationForm = UserRegistrationForm({})
        self.assertFalse(registrationForm.is_valid())

    # Test for full input of form.
    # Output: Not a valid form
    def test_full_form(self):
        registrationForm = UserRegistrationForm({
            'username': 'Kenny',
            'email': 'testingBidlet@gmail.com',
            'email2': 'testingBidlet@gmail.com',
            'password': 'password',
            'password2': 'password',
            'first_name': 'kenny',
            'last_name': 'chan',
        })
        self.assertTrue(registrationForm.is_valid())
        registration = registrationForm.save(commit=False)
        self.assertEqual(registration.username, "Kenny")
        self.assertEqual(registration.email, "testingBidlet@gmail.com")
        self.assertEqual(registration.password, "password")
        self.assertEqual(registration.first_name, "kenny")
        self.assertEqual(registration.last_name, "chan")

    def test_username_field_required(self):
        fields = {
            'email': 'testingBidlet@gmail.com',
            'email2': 'testingBidlet@gmail.com',
            'password': 'password',
            'password2': 'password',
            'first_name': 'kenny',
            'last_name': 'chan',
        }
        form = UserRegistrationForm(fields)
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required', str(form.errors["username"]))

    def test_email_field_required(self):
        fields = {
            'username': 'kenny',
            'email2': 'testingBidlet@gmail.com',
            'password': 'password',
            'password2': 'password',
            'first_name': 'kenny',
            'last_name': 'chan',
        }
        form = UserRegistrationForm(fields)
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required', str(form.errors["email"]))

    def test_email2_field_required(self):
        fields = {
            'username': 'kenny',
            'email': 'testingBidlet@gmail.com',
            'password': 'password',
            'password2': 'password',
            'first_name': 'kenny',
            'last_name': 'chan',
        }
        form = UserRegistrationForm(fields)
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required', str(form.errors["email2"]))

    def test_password_field_required(self):
        fields = {
            'username': 'kenny',
            'email': 'testingBidlet@gmail.com',
            'email2': 'testingBidlet@gmail.com',
            'password2': 'password',
            'first_name': 'kenny',
            'last_name': 'chan',
        }
        form = UserRegistrationForm(fields)
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required', str(form.errors["password"]))

    def test_password2_field_required(self):
        fields = {
            'username': 'kenny',
            'email': 'testingBidlet@gmail.com',
            'email2': 'testingBidlet@gmail.com',
            'password': 'password',
            'first_name': 'kenny',
            'last_name': 'chan',
        }
        form = UserRegistrationForm(fields)
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required', str(form.errors["password2"]))

# Black box testing on the age
class UserAccountRegistrationForm(TestCase):

    # Equivalent class 1: Under the age of 16
    # Equivalent class 2: Over the age of 16

    # Test case 1: Born today (0 age old)
    # Test case 2: Adjacent to boundary value (15 years and 364 days)
    # Test case 3: Boundary value (16 years old)
    # Test case 4: Adjacent to boundary value class 2 (16 years and one day)
    # Test case 5: Born in 1987 (30 year old)
    def test_age_born_today(self):
        birth_date = datetime.today();
        registrationForm = AccountRegistrationForm({
            'birth_date': birth_date
        })
        self.assertFalse(registrationForm.is_valid())

    def test_age_one_day_under(self):
        birth_date = datetime.today() + timedelta(days=1) - relativedelta(years=16)
        registrationForm = AccountRegistrationForm({
            'birth_date': birth_date
        })
        self.assertFalse(registrationForm.is_valid())

    def test_age_of_age_today(self):
        birth_date = datetime.today() - relativedelta(years=16)
        registrationForm = AccountRegistrationForm({
            'birth_date': birth_date
        })
        self.assertTrue(registrationForm.is_valid())

    def test_age_one_day_over(self):
        birth_date = datetime.today() - relativedelta(years=16) - timedelta(days=1)
        registrationForm = AccountRegistrationForm({
            'birth_date': birth_date
        })
        self.assertTrue(registrationForm.is_valid())

    def test_age_old(self):
        birth_date = datetime.today() - relativedelta(years=30)
        registrationForm = AccountRegistrationForm({
            'birth_date': birth_date
        })
        self.assertTrue(registrationForm.is_valid())
