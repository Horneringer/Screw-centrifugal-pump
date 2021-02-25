from django import forms
from .models import Pump


class HtmlForm(forms.Form):
    component = forms.CharField(label='Компонент')
    flow_pump = forms.FloatField(label='Расход')
    out_pressure = forms.FloatField(label='Давление на выходе')
    in_pressure = forms.FloatField(label='Давление на входе')
    steam_pressure = forms.FloatField(label='Давление насыщенного пара')
    in_temperature = forms.IntegerField(label='Температура на входе')
    density = forms.FloatField(label='Плотность компонента')
    viscosity = forms.FloatField(label='Вязкость компонента')


# форма для исходных данных насоса

class PumpForm(forms.ModelForm):
    #  поле типа ModelChoiceField позволяет выбирать только из существующих значений/наименований
    component = forms.CharField(required=True, label='Компонент', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Рабочее тело насоса'}))

    flow_pump = forms.FloatField(required=True, label='Расход', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Массовый расход, кг/с'}))

    out_pressure = forms.FloatField(required=True, label='Давление на выходе', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Давление на выходе, бар'}))

    in_pressure = forms.FloatField(required=True, label='Давление на входе', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Давление на входе, бар'}))

    steam_pressure = forms.FloatField(required=True, label='Давление насыщенного пара', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Давление насыщенного пара, бар'}))

    in_temperature = forms.IntegerField(required=True, label='Температура на входе', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Температура на входе, К'}))

    density = forms.FloatField(required=True, label='Плотность компонента', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Плотность компонента, кг/м^3'}))

    viscosity = forms.FloatField(required=True, label='Вязкость компонента', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Вязкость компонента, Па*с'}))

    # in_speed = forms.IntegerField(required=True, label='Скорость на входе', widget=forms.NumberInput(
    #   attrs={'class': 'form-control', 'placeholder': 'Скорость на входе, м/с'}))

    class Meta(object):
        model = Pump
        fields = (
            'component', 'flow_pump', 'out_pressure', 'in_pressure', 'steam_pressure', 'in_temperature', 'density',
            'viscosity',)
