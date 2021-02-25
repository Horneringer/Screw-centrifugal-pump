from django.shortcuts import render
from math import sqrt, pi, atan, tan, sin, cos, acos, ceil, radians, degrees
from numpy import cbrt
from sympy.solvers import solve
from sympy import Symbol
from numpy import rad2deg, deg2rad
import matplotlib.pyplot as plt

# данный метод выполняет указанный шаблон с переданным словарем контекста и возвращает HttpResponse с полученным
# содержимым.
from django.shortcuts import render_to_response

from .models import Pump

# после созданиея формы PumpForm пишем её вместо HtmlForm
from .forms import PumpForm


# алгоритм расчёта насоса
# -------------------------------------------------------------------------------------------------------------------------------------------------
def CalcPump(comp, fl_p, out_p, in_p, st_p, in_temp, den, vis):
    # БД компонентов и их свойств будет расширяться

    ox_lst = ['АК', 'Кислород', 'Перекись водорода', 'АТ', 'АК-20', 'АК-27']
    fuel_lst = ['Водород', 'Гидразин', 'Керосин', 'Ксилидин', 'Метан', 'НДМГ', 'Триэтиламин', 'ТГ-02']

    # ------------------------------------------------------------------------------Константы для ввода пользователем---------------------------------

    # допустимое напряжение на кручение
    allow_stress = 4 * 10 ** 8

    # коэф запаса прочности
    safety_factor = 1.3

    # скорость на входе и выходе
    # в зависимости от компонента(водород или нет) осуществить валидацию введенных данных в поле в соответствии с диапазоном
    # если водород: in_speed = 15..35 м/с; out_speed = 30..60 м/с
    # если другой компонент: in_speed = 5..10 м/с; out_speed =  15..30 м/с

    in_speed = 10
    out_speed = 23

    # резерв по давлению берут в пределах 10..30 Дж/кг

    pressure_reserve = 20

    # соотношение площади входа в центробежное колесо и площади входа на лопатки
    # выбор в пределах 0.65..08

    hee = 0.7

    # коэф влияния конечного числа лопаток 0.8..0.25

    kz = 0.825

    # гидравлический КПД 0.8..0.85

    nug = 0.82

    # расходный параметр 0.05..0.1

    qp = 0.075

    # гидравлический КПД шнека 0.4..0.7

    nug_auger = 0.65

    # коэффициент кавитационного запаса

    cavitation_factor = 1.15

    # относительная величина падения напора

    relative_head_drop = 0.15

    # число лопаток шнека 2 или 3 (увеличение приводит к снижению антикавитационных качеств и шнек делают короче)

    number_auger_blades = 2

    # оптимальное значение длины лопатки шнека 2..3

    optimal_length_auger_blade = 3

    # угол подрезки шнека на входе(для увеличения антикавитационных качеств) 90..120 градусов, далее переводим в радианы

    auger_cutting_angle_in = deg2rad(105)

    # угол подрезки шнека на выходе (для увеличения стойкости лопаток к колебаниям) 140..160 градусов, далее переводим в радианы

    auger_cutting_angle_out = deg2rad(150)

    # коэфы диаметра подвода D 1.02..1.05 и d 1.05..1.1

    wire_diameter_D_factor = 1.035

    wire_diameter_d_factor = 1.075

    # коэф скорости на входе в подвод 1.15..1.20

    speed_coeff_in_inlet = 1.2

    # коэф диаметра входа 1.07..1.1

    inlet_diameter_coeff = 1.1

    # коэфф a0 0.002..0.004 и b0

    a0 = 0.03

    b0 = 0.115

    # коэф потерь в подводе

    supply_loss_coefficient = 0.4

    # угол атаки 5..15

    attack_angle = deg2rad(10)

    # соотношение относительных скоростей на выходе и на входе 0.7..1

    ratio_relative_speeds_out_in = 0.85

    # коэф радиуса безлопаточного диффузора 1.04..1.08

    kr = 1.06

    # коэф ширины ЛНА 1.1..1.2

    kb3 = 1.15

    # константа входного угла лопаток в градусах 0..-2

    alpha0 = 1

    # константа выходного угла лопатки в градусах 5..15

    alpha01 = 10

    # густота решетки ЛНА 1.3..1.8

    tau_avg = 1.65

    # коэф выходного диаметра ЛНА 1.15..1.35

    out_diameter_coefficient = 1.25

    # коэф ширины на выходе ЛНА 1..1.2

    kb4 = 1.1

    # коэф окружной скорости на выходном сечении при наличии ЛНА 0.65..075; при отсутствии ЛНА 0.6..07

    coef_peripheral_speed_out_section_vane_guiding_device = 0.7

    coef_peripheral_speed_out_section = 0.65

    # скорость выхода 15..30

    exit_speed = 25

    # угол раскрытия диффузора 6..12

    diffuser_opening_angle = 9

    # коэф потерь в подводе; для прямоугольного и коленообразного 0.2..0.3; для кольцевого и полуспирального 0.4..0.6

    supply_loss_rate = 0.45

    # коэф потерь в колесе 0.3..0.6; для двигателя большой тяги 0.3; для двигателей малой тяги 0.6

    wheel_loss_coefficient = 0.3

    # коэф потерь в сборнике 0.1..0.15

    loss_rate_collection = 0.12

    # -----------------------------------------------------Параметры, зависящие от компонента---------------------------------------------------------------

    # коэф быстроходности
    speed_coefficient = 0

    # эквивалентный коэф диаметра шнека
    eq_coeff_of_auger_diam = 0

    # относительный диаметр втулки
    # в пределах 0.35..0.55 с радиальным подводом; 0.25..0.35 - с осевым подводом
    # необходимо реализовать зависимость коэфф от подвода и компонента; ИСПРАВИТЬ величину в курсовой и далее в коде!

    relative_diameter_sleeve = 0

    # если компонент - окислитель
    if comp in ox_lst:
        #  выбор в пределах 60..110
        speed_coefficient = 85
        eq_coeff_of_auger_diam = 9.8 - 0.04 * speed_coefficient
        relative_diameter_sleeve = 0.38

    # если компонент - горючее
    elif comp in fuel_lst:
        # выбор в пределах 30..70
        speed_coefficient = 50
        eq_coeff_of_auger_diam = 8.6 - 0.04 * speed_coefficient
        relative_diameter_sleeve = 0.4

    print(speed_coefficient)

    # -------------------------------------- Определение угловой скорости и диаметра шнека ---------------------------------------------------------------

    # объемный расход
    vol = fl_p / den

    # напор; давление, заданное в барах переводится в Па
    head = ((out_p - in_p) * 10 ** 5 / den) + ((out_speed ** 2 - in_speed ** 2) / 2)

    # угловая скорость вращения - вариант с БНА
    # добавить вариант расчёта без БНА + выбор пользователя(использовать чекбокс)

    rotational_speed = (speed_coefficient * (head ** 0.75)) / (193.3 * sqrt(vol))

    # КПД насоса

    pump_efficiency = (0.82 - 0.005 * sqrt(speed_coefficient)) / (1 + (500 / speed_coefficient ** 2))

    # полная располагаемая энергия на входе в насос

    total_available_energy_in = ((in_p * 10 ** 5 - st_p * 10 ** 5) / den) + in_speed ** 2 / 2

    # допускаемый кавитационный запас

    allowable_stock = total_available_energy_in - pressure_reserve

    # коэффициент диаметра шнека

    coeff_of_auger_diam = eq_coeff_of_auger_diam / sqrt(1 - relative_diameter_sleeve ** 2)

    # диаметр шнека

    auger_diam = 0.47 * coeff_of_auger_diam * cbrt(vol / rotational_speed)

    # эквивалентный диаметр шнека

    eq_auger_diam = 0.47 * eq_coeff_of_auger_diam * cbrt(vol / rotational_speed)

    # диаметр втулки

    sleeve_diam = auger_diam * relative_diameter_sleeve

    # --------------------------------------------------------Определение размеров входа в центробежное колесо----------------------------------------------

    # коэффициент эквивалентного входного диаметра колеса
    # eq_coeff_of_auger_diam домножается на коэфф изм в пределах (0.7..1)
    # чем выше коэф быстроходности, тем коэф ближе к 0.7 и меньше величина eq_wheel_diam_in

    eq_coeff_wheel_diam_in = 0.9 * eq_coeff_of_auger_diam

    # коэффициент входного диаметра колеса

    coeff_wheel_diam_in = eq_coeff_wheel_diam_in / sqrt(1 - relative_diameter_sleeve ** 2)

    # входной диаметр колеса
    wheel_diam_in = 0.47 * coeff_wheel_diam_in * cbrt(vol / rotational_speed)

    # средний диаметр входных кромок лопаток центробежного колеса
    # коэф в пределах 0.85..0.95(добавить условие на выбор)

    avg_diam_edges_blades_wheel_in = 0.9 * wheel_diam_in

    # эквивалентный входной диаметр

    eq_wheel_diam_in = sqrt((wheel_diam_in ** 2) - (sleeve_diam ** 2))

    # ширина колеса на входе

    width_wheel_in = (eq_wheel_diam_in ** 2) / (4 * hee * avg_diam_edges_blades_wheel_in)

    # окружная скорость колеса на выходе

    wheel_outlet_peripheral_speed = sqrt(head / (kz * nug * (1 - qp)))

    # средний диаметр выходных кромок лопаток

    avg_diam_edges_blades_wheel_out = 2 * wheel_outlet_peripheral_speed / rotational_speed

    # отношение диаметров

    diameter_ratio = avg_diam_edges_blades_wheel_in / avg_diam_edges_blades_wheel_out

    # средний диаметр шнека

    average_screw_diameter = (auger_diam + sleeve_diam) / 2

    # окружная скорость на среднем диаметре

    peripheral_speed_middle_diameter = rotational_speed * average_screw_diameter / 2

    # относительный кавитационный запас

    relative_suction_head = allowable_stock / peripheral_speed_middle_diameter ** 2

    # осевая скорость на входе в шнек

    axial_speed_auger_in = (4 * vol) / (pi * (eq_auger_diam ** 2))

    # осевая скорость на выходе из шнека

    axial_speed_auger_out = axial_speed_auger_in

    # относительная осевая скорость

    relative_axial_velocity = axial_speed_auger_out / peripheral_speed_middle_diameter

    # необходимая относительная закрутка потока на выходе из шнека
    # находится из уравнения

    x = Symbol('x')
    required_relative_flow_swirl_out_screw = solve(
        relative_suction_head + nug_auger * x - relative_head_drop - 0.5 * cavitation_factor * hee * (
                average_screw_diameter / avg_diam_edges_blades_wheel_in) * (relative_axial_velocity / (
                1 - x * (average_screw_diameter / avg_diam_edges_blades_wheel_in) ** 2))
        * ((
                   avg_diam_edges_blades_wheel_in / average_screw_diameter - x * average_screw_diameter / avg_diam_edges_blades_wheel_in) ** 2 + hee ** 2 * x ** 2) - 0.5 * hee ** 2 * relative_axial_velocity ** 2 - 0.5 * x ** 2 * (
                average_screw_diameter / avg_diam_edges_blades_wheel_in) ** 2, x)[0]

    required_relative_flow_swirl_out_screw = round(required_relative_flow_swirl_out_screw, 2)

    # угол потока на выходе из шнека

    flow_angle_out_screw = rad2deg(atan(relative_axial_velocity / (1 - required_relative_flow_swirl_out_screw)))

    # эквивалентный шаг шнека

    equivalent_auger_pitch = pi * average_screw_diameter * tan(flow_angle_out_screw)

    # угол входа потока в шнек

    angle_flow_in_auger = rad2deg(atan(relative_axial_velocity))

    # угол атаки на среднем диаметре

    angle_attack_medium_diameter = (flow_angle_out_screw - angle_flow_in_auger)

    # если угол атаки на среднем диаметре < 10, то можно применить шнек постоянного шага

    # густота решетки

    lattice_density = optimal_length_auger_blade * number_auger_blades / pi

    # осевая длина шнека на среднем диаметре(для постоянного шага S, для переменного Sэ)

    axial_length_screw_middle_diameter = (pi * average_screw_diameter * lattice_density) / number_auger_blades * sin(
        atan(equivalent_auger_pitch / (pi * average_screw_diameter)))

    # осевая длина шнека у втулки

    axial_length_screw_sleeve = axial_length_screw_middle_diameter + (((average_screw_diameter - sleeve_diam) / 2) * ((
                                                                                                                              cos(
                                                                                                                                  (
                                                                                                                                      auger_cutting_angle_in) / 2) / sin(
                                                                                                                          (
                                                                                                                              auger_cutting_angle_in) / 2)) + (
                                                                                                                              cos(
                                                                                                                                  (
                                                                                                                                      auger_cutting_angle_out) / 2) / sin(
                                                                                                                          (
                                                                                                                              auger_cutting_angle_out) / 2))))

    # кольцевой подвод

    # диаметры подвода

    inlet_diameter_D = wire_diameter_D_factor * auger_diam

    inlet_diameter_d = wire_diameter_d_factor * sleeve_diam

    # скорость на входе в подвод

    inlet_speed = axial_speed_auger_in / speed_coeff_in_inlet

    # диаметр входа

    inlet_diameter = inlet_diameter_coeff * sqrt(auger_diam ** 2 - sleeve_diam ** 2)

    # коэф кавитации шнека

    screw_cavitation_coeff = a0 + b0 * relative_axial_velocity

    # срывной кавитационный запас

    breakaway_cavitation_reserve = ((
                                            1 + supply_loss_coefficient) * axial_speed_auger_in ** 2 / 2) + (
                                           screw_cavitation_coeff * (
                                           peripheral_speed_middle_diameter ** 2 + axial_speed_auger_in ** 2) / 2)

    # меридиональная скорость на входе в колесо

    meridional_speed_wh_in = hee * axial_speed_auger_out

    # окружная скорость на входе в колесо

    peripheral_speed_wheel_in = peripheral_speed_middle_diameter * (
            avg_diam_edges_blades_wheel_in / average_screw_diameter)

    # окружная составляющая абсолютной скорости потока на выходе из шнека

    circum_component_absolute_flow_rate_out_screw = required_relative_flow_swirl_out_screw * peripheral_speed_middle_diameter

    # окружная составляющая абсолютной скорости потока на входе в колесо

    circum_component_abs_flow_velocity_wheel_in = circum_component_absolute_flow_rate_out_screw * (
            avg_diam_edges_blades_wheel_in / average_screw_diameter)

    # угол потока на входе в колесо

    wheel_in_flow_angle = rad2deg(
        atan(meridional_speed_wh_in / (peripheral_speed_wheel_in - circum_component_abs_flow_velocity_wheel_in)))

    wheel_in_flow_angle = round(wheel_in_flow_angle, 1)

    # входной угол лопаток колеса

    wheel_entry_angle = (wheel_in_flow_angle + rad2deg(attack_angle))

    # угол лопаток на выходе

    wheel_out_angle = rad2deg(acos((
                                           pi * wheel_outlet_peripheral_speed * avg_diam_edges_blades_wheel_in * width_wheel_in * qp * sin(
                                       deg2rad(wheel_entry_angle))) / ratio_relative_speeds_out_in * vol))

    wheel_out_angle = round(wheel_out_angle, 1)

    # ширина колеса на выходе

    width_wheel_out = ((avg_diam_edges_blades_wheel_in * width_wheel_in) / (
            ratio_relative_speeds_out_in * avg_diam_edges_blades_wheel_out)) * sin(
        wheel_entry_angle / wheel_out_angle)

    width_wheel_out = round(width_wheel_out, 4)

    # меридиональная скорость на выходе из колеса

    meridional_speed_wheel_out = vol / (pi * avg_diam_edges_blades_wheel_out * width_wheel_out)

    # количество лопаток колеса

    number_wheel_blades = ceil(3 * (1.5 + (wheel_out_angle / 60)) + 130 * (diameter_ratio - 0.6) ** 2)

    # закрутка потока на выходе из колеса

    swirling_flow_wheel_out = wheel_outlet_peripheral_speed - (meridional_speed_wheel_out / tan(wheel_out_angle))

    # закрутка потока с учётом конечного числа лопаток

    swirling_flow_finite_number_blades = kz * swirling_flow_wheel_out

    # если u2 > 200 м/с, то расчитывается ЛНА, иначе ячейки таблицы пустые (структура таблицы отображается в любом случае)

    # wheel_outlet_peripheral_speed = 222

    # выходной радиус безлопаточного диффузора

    vaneless_diffuser_out_radius = kr * (avg_diam_edges_blades_wheel_out / 2)

    if wheel_outlet_peripheral_speed > 200:

        # входной угол средней линии лопаток ЛНА

        centerline_entry_angle = rad2deg(atan(meridional_speed_wheel_out / swirling_flow_finite_number_blades))

        # ширина ЛНА на входе

        width_vane_guiding_device = kb3 * width_wheel_out

        # угол входа потока в ЛНА

        flow_entry_angle_vane_guiding_device = rad2deg(atan((width_wheel_out / width_vane_guiding_device) * (
                1.5 - 0.5 * (width_wheel_out / width_vane_guiding_device)) * tan(centerline_entry_angle)))

        # входной угол лопаток ЛНА

        blade_entry_angle_vane_guiding_device = flow_entry_angle_vane_guiding_device + alpha0

        # выходной угол лопаток ЛНА

        out_angle_blades_vane_guiding_device = blade_entry_angle_vane_guiding_device + alpha01

        # выходной диаметр ЛНА

        outlet_diameter_vane_guiding_device = 2 * vaneless_diffuser_out_radius * out_diameter_coefficient

        # длина хорды лопатки

        blade_chord_length = outlet_diameter_vane_guiding_device - (vaneless_diffuser_out_radius * 2) / (
                2 * rad2deg(sin(blade_entry_angle_vane_guiding_device + out_angle_blades_vane_guiding_device)) / 2)

        # шаг на среднем диаметре

        pitch_avg_diameter = blade_chord_length / tau_avg

        # число лопаток ЛНА

        number_blades_vane_guiding_device = ceil(
            pi * (vaneless_diffuser_out_radius * 2 + outlet_diameter_vane_guiding_device) / (2 * pitch_avg_diameter))

        # ширина ЛНА на выходе

        out_width_vane_guiding_device = width_vane_guiding_device * kb4

        # меридиональная скорость на выходе из ЛНА

        meridional_out_velocity_vane_guiding_device = vol / (
                pi * outlet_diameter_vane_guiding_device * out_width_vane_guiding_device)

        #  окружная скорость на выходе из ЛНА

        peripheral_out_speed_vane_guiding_device = meridional_out_velocity_vane_guiding_device / tan(
            out_angle_blades_vane_guiding_device)

        # окружная скорость на выходном сечении

        peripheral_speed_out = coef_peripheral_speed_out_section_vane_guiding_device * peripheral_out_speed_vane_guiding_device

    else:
        centerline_entry_angle = 'NONE'
        width_vane_guiding_device = 'NONE'
        flow_entry_angle_vane_guiding_device = 'NONE'
        blade_entry_angle_vane_guiding_device = 'NONE'
        out_angle_blades_vane_guiding_device = 'NONE'
        outlet_diameter_vane_guiding_device = 'NONE'
        blade_chord_length = 'NONE'
        pitch_avg_diameter = 'NONE'
        number_blades_vane_guiding_device = 'NONE'
        out_width_vane_guiding_device = 'NONE'
        meridional_out_velocity_vane_guiding_device = 'NONE'
        peripheral_out_speed_vane_guiding_device = 'NONE'
        peripheral_speed_out = coef_peripheral_speed_out_section * swirling_flow_finite_number_blades

    # площадь выходного сечения(горла)

    outlet_area = vol / peripheral_speed_out

    # список углов в различных сечениях

    angles_various_sections = [30, 90, 180, 270, 350]

    # площадь спирали в любом произвольном сечении

    spiral_area_any_arbitrary_section = [outlet_area * (angle / 360) for angle in
                                         angles_various_sections]

    spiral_area_any_arbitrary_section = [round(area, 7) for area in spiral_area_any_arbitrary_section]

    spiral_area_any_arbitrary_section = ', '.join(str(area) for area in spiral_area_any_arbitrary_section)

    # диаметр горла спирали

    spiral_neck_diameter = sqrt(4 * outlet_area / pi)

    # радиус внешней стенки спирали

    spiral_outer_wall_radius = [vaneless_diffuser_out_radius + spiral_neck_diameter * sqrt(angle / 360) for angle in
                                angles_various_sections]

    spiral_outer_wall_radius = [round(radius, 3) for radius in spiral_outer_wall_radius]

    spiral_outer_wall_radius = ', '.join(str(radius) for radius in spiral_outer_wall_radius)

    # площадь выходного сечения

    outlet_area_diff = vol / exit_speed

    # диаметр выходного сечения

    outlet_diameter = sqrt(4 * outlet_area_diff / pi)

    # эквивалентный диаметр горла

    equivalent_throat_diameter = sqrt(4 * outlet_area / pi)

    # длина конического диффузора на ходится из уравнения

    x = Symbol('x')

    conical_diffuser_length = solve(
        tan(radians(diffuser_opening_angle / 2)) - (outlet_diameter - equivalent_throat_diameter) / (2 * x), x)[0]

    if conical_diffuser_length > 6.5 * equivalent_throat_diameter:
        conical_diffuser_length = str(conical_diffuser_length) + ' следует применить ступенчатый диффузор!'

    # потери энергии в подводе

    loss_energy_supply = (supply_loss_rate * axial_speed_auger_in ** 2) / 2

    # относительная скорость на входе в центробежное колесо

    relative_speed_entrance_centrifugal_wheel = sqrt(
        meridional_speed_wh_in ** 2 + (peripheral_speed_wheel_in - circum_component_abs_flow_velocity_wheel_in) ** 2)

    # потери энергии в шнеке

    energy_loss_screw = (
                                1 - nug_auger) * circum_component_absolute_flow_rate_out_screw * peripheral_speed_middle_diameter

    # потери энергии в центробежном колесе

    energy_loss_centrifugal_wheel = wheel_loss_coefficient * ((relative_speed_entrance_centrifugal_wheel ** 2) / 2)

    # при отсутствии ЛНА

    # потери энергии в спиральном сборнике
    energy_losses_spiral_collector = loss_rate_collection * (swirling_flow_finite_number_blades ** 2) / 2

    # коэфф потерь конического диффузора со ступенчатым входом

    loss_factor_conical_diffuser_stepped_inlet = 1.15 * tan(radians(diffuser_opening_angle)) * cbrt(
        outlet_area_diff / outlet_area - 1)

    # потери в коническом диффузоре

    conical_diffuser_loss = loss_factor_conical_diffuser_stepped_inlet * (peripheral_speed_out ** 2) / 2

    # гидравлические потери в шнекоцентробежном насосе

    hydraulic_losses_screw_centrifugal_pump = loss_energy_supply + energy_loss_screw + energy_loss_centrifugal_wheel + energy_losses_spiral_collector + conical_diffuser_loss

    # теоретический напор

    theoretical_head = head + hydraulic_losses_screw_centrifugal_pump

    # гидравлический кпд насоса

    hydraulic_pump_efficiency = head / theoretical_head

    # ---------------------------------------------------------------------------------------Построение графиков энергетических характеристик-----------------------------------------------------------

    # коэффициенты режимов
    mode_coefficients = [0, 1 / 5, 2 / 5, 3 / 5, 4 / 5, 1, 6 / 5, 7 / 5]

    # расходы на расчётных режимах

    flow_rate_design_modes = [vol * coeff for coeff in mode_coefficients]

    print(flow_rate_design_modes)

    # расходный параметр

    consumption_parameter = 1 / (1 + (2 * pi * head * width_wheel_out * tan(wheel_entry_angle) / (
            vol * rotational_speed * kz * hydraulic_pump_efficiency))) / 10

    # действительный напор через насос на расчётном режиме

    actual_head_flow = [(1.06 + 0.8 * consumption_parameter * (1 - (rate / vol)) - 0.296 * (0.55 * (rate / vol)) ** 2)
                        for rate in flow_rate_design_modes]

    # относительный КПД

    relative_efficiency = [((2.69 * (rate / vol)) - (2.65 * ((rate / vol) ** 2)) + (1.22 * ((rate / vol) ** 3)) - (
            0.26 * ((rate / vol) ** 4))) for rate in flow_rate_design_modes]

    # мощностная характеристика насоса

    pump_power_characteristic = [
        (1.06 + 0.8 * consumption_parameter * (1 - (rate / vol)) - 0.296 * (0.55 - (rate / vol) ** 2)) / (
                2.69 - 2.65 * (rate / vol) + 1.22 * (rate / vol) ** 2 - 0.26 * (rate / vol) ** 3) for rate in
        flow_rate_design_modes]

    print(actual_head_flow)
    print(relative_efficiency)
    print(pump_power_characteristic)

    plt.title("Зависимость напора насоса от расхода")
    plt.xlabel("Vрас")
    plt.ylabel("Нотн")
    plt.grid()
    plt.plot(flow_rate_design_modes, actual_head_flow)
    plt.show()

    plt.title("Зависимость КПД насоса от расхода")
    plt.xlabel("Vрас")
    plt.ylabel(chr(951))
    plt.grid()
    plt.plot(flow_rate_design_modes, relative_efficiency)
    plt.show()

    plt.title("Зависимость мощности насоса от расхода")
    plt.xlabel("Vрас")
    plt.ylabel("Nотн")
    plt.grid()
    plt.plot(flow_rate_design_modes, pump_power_characteristic)
    plt.show()

    return vol, head, rotational_speed, pump_efficiency, total_available_energy_in, allowable_stock, eq_coeff_of_auger_diam, coeff_of_auger_diam, \
           auger_diam, eq_auger_diam, sleeve_diam, eq_coeff_wheel_diam_in, coeff_wheel_diam_in, wheel_diam_in, avg_diam_edges_blades_wheel_in, eq_wheel_diam_in, width_wheel_in, wheel_outlet_peripheral_speed, avg_diam_edges_blades_wheel_out, \
           diameter_ratio, average_screw_diameter, peripheral_speed_middle_diameter, relative_suction_head, axial_speed_auger_in, relative_axial_velocity, required_relative_flow_swirl_out_screw, flow_angle_out_screw, \
           equivalent_auger_pitch, angle_flow_in_auger, angle_attack_medium_diameter, lattice_density, axial_length_screw_middle_diameter, axial_length_screw_sleeve, inlet_diameter_D, \
           inlet_diameter_d, inlet_speed, inlet_diameter, screw_cavitation_coeff, breakaway_cavitation_reserve, meridional_speed_wh_in, peripheral_speed_wheel_in, circum_component_absolute_flow_rate_out_screw, \
           circum_component_abs_flow_velocity_wheel_in, wheel_in_flow_angle, wheel_entry_angle, wheel_out_angle, width_wheel_out, meridional_speed_wheel_out, number_wheel_blades, swirling_flow_wheel_out, \
           swirling_flow_finite_number_blades, vaneless_diffuser_out_radius, centerline_entry_angle, width_vane_guiding_device, flow_entry_angle_vane_guiding_device, blade_entry_angle_vane_guiding_device, \
           out_angle_blades_vane_guiding_device, outlet_diameter_vane_guiding_device, blade_chord_length, pitch_avg_diameter, number_blades_vane_guiding_device, out_width_vane_guiding_device, \
           meridional_out_velocity_vane_guiding_device, peripheral_out_speed_vane_guiding_device, peripheral_speed_out, outlet_area, spiral_area_any_arbitrary_section, spiral_neck_diameter, spiral_outer_wall_radius, \
           outlet_area_diff, outlet_diameter, equivalent_throat_diameter, conical_diffuser_length, loss_energy_supply, relative_speed_entrance_centrifugal_wheel, energy_loss_screw, \
           energy_loss_centrifugal_wheel, energy_losses_spiral_collector, loss_factor_conical_diffuser_stepped_inlet, conical_diffuser_loss, hydraulic_losses_screw_centrifugal_pump, theoretical_head, hydraulic_pump_efficiency, \
           consumption_parameter


# -------------------------------------------------------------------------------------------------------------------------------------------------


# функция отображения страницы с формой ввода данных насоса
def home(request):
    if request.method == 'POST':
        form = PumpForm(request.POST or None)
        # если форма валидна
        if form.is_valid():
            # отображается содержимое формы
            # print(form.cleaned_data)
            # print(form.cleaned_data['component'])

            component = form.cleaned_data['component']
            flow_pump = form.cleaned_data['flow_pump']
            out_pressure = form.cleaned_data['out_pressure']
            in_pressure = form.cleaned_data['in_pressure']
            steam_pressure = form.cleaned_data['steam_pressure']
            in_temperature = form.cleaned_data['in_temperature']
            density = form.cleaned_data['density']
            viscosity = form.cleaned_data['viscosity']

            print(
                'Компонент: {} \n'
                'Массовый расход: {} \n'
                'Давление на выходе:{} \n'
                'Давление на входе:{} \n'
                'Давление насыщенного пара:{} \n'
                'Температура на входе: {} \n'
                'Плотность компонента: {} \n'
                'Вязкость компонента: {} \n'.format(
                    component, flow_pump, out_pressure, in_pressure, steam_pressure, in_temperature, density,
                    viscosity))

            volume_flow, Head, rot_sp, p_eff, tot_av_en, al_stock, eq_coeff_aug, coeff_aug, aug_diam, eq_aug_diam, sl_diam, eq_coeff_w_diam_in, coeff_w_diam_in, w_diam_in, avg_diam_ed_bl_w_in, eq_w_diam_in, width_w_in, w_out_peripheral_speed, \
            avg_diam_ed_bl_w_out, diam_rat, avg_screw_diam, peripheral_speed_mid_diam, relative_suction_head, axial_speed_auger_in, relative_axial_velocity, required_relative_flow_swirl_out_screw, \
            flow_angle_out_screw, equivalent_auger_pitch, angle_flow_in_auger, angle_attack_medium_diameter, lattice_density, axial_length_screw_middle_diameter, axial_length_screw_sleeve, \
            inlet_diameter_D, inlet_diameter_d, inlet_speed, inlet_diameter, screw_cavitation_coeff, breakaway_cavitation_reserve, meridional_speed_wh_in, peripheral_speed_wheel_in, \
            circum_component_absolute_flow_rate_out_screw, circum_component_abs_flow_velocity_wheel_in, wheel_in_flow_angle, wheel_entry_angle, wheel_out_angle, width_wheel_out, meridional_speed_wheel_out, \
            number_wheel_blades, swirling_flow_wheel_out, swirling_flow_finite_number_blades, vaneless_diffuser_out_radius, centerline_entry_angle, width_vane_guiding_device, \
            flow_entry_angle_vane_guiding_device, blade_entry_angle_vane_guiding_device, out_angle_blades_vane_guiding_device, outlet_diameter_vane_guiding_device, blade_chord_length, pitch_avg_diameter, \
            number_blades_vane_guiding_device, out_width_vane_guiding_device, meridional_out_velocity_vane_guiding_device, peripheral_out_speed_vane_guiding_device, peripheral_speed_out, outlet_area, \
            spiral_area_any_arbitrary_section, spiral_neck_diameter, spiral_outer_wall_radius, outlet_area_diff, outlet_diameter, equivalent_throat_diameter, conical_diffuser_length, \
            loss_energy_supply, relative_speed_entrance_centrifugal_wheel, energy_loss_screw, energy_loss_centrifugal_wheel, energy_losses_spiral_collector, loss_factor_conical_diffuser_stepped_inlet, conical_diffuser_loss, \
            hydraulic_losses_screw_centrifugal_pump, theoretical_head, hydraulic_pump_efficiency, consumption_parameter = CalcPump(
                component,
                flow_pump,
                out_pressure,
                in_pressure,
                steam_pressure,
                in_temperature,
                density,
                viscosity)
            # возврат шаблона с результатом
            # ИСПРАВИТЬ! не отображает в адресной строке /pump_results
            return render(request, 'pump_data/pump_results.html',
                          {'volume_flow': volume_flow, 'Head': Head, 'rot_sp': rot_sp, 'p_eff': p_eff,
                           'tot_av_en': tot_av_en, 'al_stock': al_stock, 'eq_coeff_aug': eq_coeff_aug,
                           'coeff_aug': coeff_aug, 'aug_diam': aug_diam, 'eq_aug_diam': eq_aug_diam,
                           'sl_diam': sl_diam, 'eq_coeff_w_diam_in': eq_coeff_w_diam_in,
                           'coeff_w_diam_in': coeff_w_diam_in,
                           'w_diam_in': w_diam_in, 'avg_diam_ed_bl_w_in': avg_diam_ed_bl_w_in,
                           'eq_w_diam_in': eq_w_diam_in, 'width_w_in': width_w_in,
                           'w_out_peripheral_speed': w_out_peripheral_speed,
                           'avg_diam_ed_bl_w_out': avg_diam_ed_bl_w_out, 'diam_rat': diam_rat,
                           'avg_screw_diam': avg_screw_diam, 'peripheral_speed_mid_diam': peripheral_speed_mid_diam,
                           'relative_suction_head': relative_suction_head, 'axial_speed_auger_in': axial_speed_auger_in,
                           'relative_axial_velocity': relative_axial_velocity,
                           'required_relative_flow_swirl_out_screw': required_relative_flow_swirl_out_screw,
                           'flow_angle_out_screw': flow_angle_out_screw,
                           'equivalent_auger_pitch': equivalent_auger_pitch, 'angle_flow_in_auger': angle_flow_in_auger,
                           'angle_attack_medium_diameter': angle_attack_medium_diameter,
                           'lattice_density': lattice_density,
                           'axial_length_screw_middle_diameter': axial_length_screw_middle_diameter,
                           'axial_length_screw_sleeve': axial_length_screw_sleeve,
                           'inlet_diameter_D': inlet_diameter_D, 'inlet_diameter_d': inlet_diameter_d,
                           'inlet_speed': inlet_speed, 'inlet_diameter': inlet_diameter,
                           'screw_cavitation_coeff': screw_cavitation_coeff,
                           'breakaway_cavitation_reserve': breakaway_cavitation_reserve,
                           'meridional_speed_wh_in': meridional_speed_wh_in,
                           'peripheral_speed_wheel_in': peripheral_speed_wheel_in,
                           'circum_component_absolute_flow_rate_out_screw': circum_component_absolute_flow_rate_out_screw,
                           'circum_component_abs_flow_velocity_wheel_in': circum_component_abs_flow_velocity_wheel_in,
                           'wheel_in_flow_angle': wheel_in_flow_angle, 'wheel_entry_angle': wheel_entry_angle,
                           'wheel_out_angle': wheel_out_angle, 'width_wheel_out': width_wheel_out,
                           'meridional_speed_wheel_in': meridional_speed_wheel_out,
                           'number_wheel_blades': number_wheel_blades,
                           'swirling_flow_wheel_out': swirling_flow_wheel_out,
                           'swirling_flow_finite_number_blades': swirling_flow_finite_number_blades,
                           'vaneless_diffuser_out_radius': vaneless_diffuser_out_radius,
                           'centerline_entry_angle': centerline_entry_angle,
                           'width_vane_guiding_device': width_vane_guiding_device,
                           'flow_entry_angle_vane_guiding_device': flow_entry_angle_vane_guiding_device,
                           'blade_entry_angle_vane_guiding_device': blade_entry_angle_vane_guiding_device,
                           'out_angle_blades_vane_guiding_device': out_angle_blades_vane_guiding_device,
                           'outlet_diameter_vane_guiding_device': outlet_diameter_vane_guiding_device,
                           'blade_chord_length': blade_chord_length, 'pitch_avg_diameter': pitch_avg_diameter,
                           'number_blades_vane_guiding_device': number_blades_vane_guiding_device,
                           'out_width_vane_guiding_device': out_width_vane_guiding_device,
                           'meridional_out_velocity_vane_guiding_device': meridional_out_velocity_vane_guiding_device,
                           'peripheral_out_speed_vane_guiding_device': peripheral_out_speed_vane_guiding_device,
                           'peripheral_speed_out': peripheral_speed_out, 'outlet_area': outlet_area,
                           'spiral_area_any_arbitrary_section': spiral_area_any_arbitrary_section,
                           'spiral_neck_diameter': spiral_neck_diameter,
                           'spiral_outer_wall_radius': spiral_outer_wall_radius, 'outlet_area_diff': outlet_area_diff,
                           'outlet_diameter': outlet_diameter,
                           'equivalent_throat_diameter': equivalent_throat_diameter,
                           'conical_diffuser_length': conical_diffuser_length, 'loss_energy_supply': loss_energy_supply,
                           'relative_speed_entrance_centrifugal_wheel': relative_speed_entrance_centrifugal_wheel,
                           'energy_loss_screw': energy_loss_screw,
                           'energy_loss_centrifugal_wheel': energy_loss_centrifugal_wheel,
                           'energy_losses_spiral_collector': energy_losses_spiral_collector,
                           'loss_factor_conical_diffuser_stepped_inlet': loss_factor_conical_diffuser_stepped_inlet,
                           'conical_diffuser_loss': conical_diffuser_loss,
                           'hydraulic_losses_screw_centrifugal_pump': hydraulic_losses_screw_centrifugal_pump,
                           'theoretical_head': theoretical_head,
                           'hydraulic_pump_efficiency': hydraulic_pump_efficiency,
                           'consumption_parameter': consumption_parameter})

    form = PumpForm
    return render(request, 'pump_data/home.html', {'form': form})
