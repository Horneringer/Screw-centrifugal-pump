from django.db import models


class Pump(models.Model):
    # компонент
    component = models.CharField(max_length=100, unique=False, verbose_name='Компонент')

    # расход через насос
    flow_pump = models.FloatField(verbose_name='Расход, кг/с')

    # давление на выходе
    out_pressure = models.FloatField(verbose_name='Давление на выходе, бар')

    # давление на входе
    in_pressure = models.FloatField(verbose_name='Давление на входе, бар')

    # давление насыщенного пара
    steam_pressure = models.FloatField(verbose_name='Давление насыщенного пара, бар')

    # температура на входе
    in_temperature = models.IntegerField(verbose_name='Температура на входе, К')

    # плотность компонента
    density = models.FloatField(verbose_name='Плотность компонента, кг/м^3')

    # вязкость компонента
    viscosity = models.FloatField(verbose_name='Вязкость компонента, Па*с')

    # скорость на входе
    # in_speed = model.IntegerField(verbose_name = 'Скорость на входе', м/с)
    #
    # скорость на выходе
    # out_speed = model.IntegerField(verbose_name = 'Скорость на выходе', м/с)
    #

    class Meta:
        verbose_name = 'Насос'
        verbose_name_plural = 'Насосы'
        ordering = ['pk']

    def __str__(self):
        return '{} Шнекоцентробежный насос, на компоненте \"{}\"'.format(self.pk, self.component)
