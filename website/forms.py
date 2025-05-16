from flask_wtf import FlaskForm
from wtforms import  DecimalField, EmailField, IntegerField, MultipleFileField, SelectField, StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Email



class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2)])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6)])
    phone_number = StringField('Phone Number', validators=[Optional()])  # Now it's optional
    submit = SubmitField('Sign Up')  # Submit button


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')  # Submit button


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), Length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), Length(min=6)])
    change_password = SubmitField('Change Password')  # Submit button


class ProductInventoryForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    sale_price = DecimalField('Sale Price', validators=[Optional()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Rings', 'Rings'),
    ('Necklaces', 'Necklaces'),
    ('Bracelets', 'Bracelets'),
    ('Earrings', 'Earrings'),
    ('Collections', 'Collections')], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    product_images = MultipleFileField('Product Images', validators=[Optional()])
    submit = SubmitField('Submit')


class ReviewForm(FlaskForm):
    rating = SelectField(
        'Rating',
        choices=[(str(i), f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
        validators=[DataRequired()]
    )
    review_text = TextAreaField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Submit Review')


class OrderForm(FlaskForm):
    order_status = SelectField('Order Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'),
                                                        ('Out for delivery', 'Out for delivery'),
                                                        ('Delivered', 'Delivered'), ('Canceled', 'Canceled')])
    
    update = SubmitField('Update Status')



class UpdateOrderStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')  # Submit button



class CheckoutForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[Length(min=10, max=15)])
    address = StringField("Street Address", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired()])
    zip_code = StringField("ZIP Code", validators=[DataRequired()])
    country = SelectField("Country", choices=[
        ("US", "United States"),
        ("CA", "Canada"),
        ("GB", "United Kingdom"),
        ("AU", "Australia"),
        ("OTHER", "Other"),
    ], validators=[DataRequired()])
    notes = TextAreaField("Order Notes (Optional)")
    submit = SubmitField("Place Order")