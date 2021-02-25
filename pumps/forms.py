# форма для аутентификации пользователя
from django import forms

from django.contrib.auth import authenticate


class UserLoginForm(forms.Form):
    # поля формы
    # в атрибуты передаём класс для отображения Bootstrap
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    # для пароля задаём специальный тип поля PasswordInput
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    # проверка наличия пользователя и правильность пароля
    def clean(self, *args, **kwargs):
        # через get получаем имя пользователя и пароль для проверки
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        # если все данные верны
        if username and password:
            # произвидится аутентификация
            user = authenticate(username=username, password=password)

            # если проверка не прошла(логин И пароль не верны)
            if not user:
                # выбрасываем ошибку с сообщение
                raise forms.ValidationError('Пользователь не существует!')

            # если не прошла проверка по паролю
            if not user.check_password(password):
                raise forms.ValidationError('Неверный пароль!')

        return super(UserLoginForm, self).clean(*args, **kwargs)
