from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Користувацький менеджер для створення користувачів
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

# Модель користувача
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=45, unique=True)
    firstname = models.CharField(max_length=45)
    lastname = models.CharField(max_length=45)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=45)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    isAdmin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Зміни це на унікальне ім'я
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Зміни це на унікальне ім'я
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def str(self):
        return self.email

# Модель платіжного методу
class Paymethod(models.Model):
    cardNumber = models.CharField(max_length=45, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def str(self):
        return self.cardNumber

# Модель трансферів
class Transfer(models.Model):
    TRANSFER_STATUS = (
        ('failed', 'Failed'),
        ('approved', 'Approved'),
        ('denied', 'Denied')
    )
    transferValue = models.DecimalField(max_digits=10, decimal_places=2)
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=8, choices=TRANSFER_STATUS)
    source_paymethod = models.ForeignKey(Paymethod, related_name='source_transfers', on_delete=models.CASCADE)
    destination_paymethod = models.ForeignKey(Paymethod, related_name='destination_transfers', on_delete=models.CASCADE)

    def str(self):
        return f'{self.source_paymethod} -> {self.destination_paymethod} ({self.transferValue})'

# Модель для блокування токенів
class TokenBlocklist(models.Model):
    jti = models.CharField(max_length=36, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)