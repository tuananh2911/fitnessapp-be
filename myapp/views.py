from django.http import HttpResponse
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
def caculate_tdee(gender, weight, height, age, activity_level):
    if not (gender == 'male' or gender == 'female'):
        raise ValueError("Giới tính phải là 'male' hoặc 'female'")
    if not (1.2 <= activity_level <= 1.9):
        raise ValueError("Mức độ hoạt động phải nằm trong khoảng từ 1.2 đến 1.9")

    # Công thức Harris-Benedict
    if gender == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:  # gender == 'female'
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    tdee = bmr * activity_level
    return tdee
def caculate_time_to_goal(current_wt, goal_wt):
    current_weight = ctrl.Antecedent(np.arange(40, 150, 1), 'current_weight')
    goal_weight = ctrl.Antecedent(np.arange(40, 150, 1), 'goal_weight')
    time = ctrl.Consequent(np.arange(1, 53, 1), 'time')  # Thời gian tính bằng tuần

    # Tùy chỉnh hàm thành viên
    current_weight['low'] = fuzz.trimf(current_weight.universe, [40, 40, 95])
    current_weight['medium'] = fuzz.trimf(current_weight.universe, [40, 95, 150])
    current_weight['high'] = fuzz.trimf(current_weight.universe, [95, 150, 150])

    goal_weight['low'] = fuzz.trimf(goal_weight.universe, [40, 40, 95])
    goal_weight['medium'] = fuzz.trimf(goal_weight.universe, [40, 95, 150])
    goal_weight['high'] = fuzz.trimf(goal_weight.universe, [95, 150, 150])

    time['short'] = fuzz.trimf(time.universe, [1, 1, 26])
    time['medium'] = fuzz.trimf(time.universe, [1, 26, 52])
    time['long'] = fuzz.trimf(time.universe, [26, 52, 52])

    # Xác định quy tắc mờ
    rule1 = ctrl.Rule(current_weight['low'] & goal_weight['high'], time['long'])
    rule2 = ctrl.Rule(current_weight['high'] & goal_weight['low'], time['long'])
    rule3 = ctrl.Rule(current_weight['medium'] & goal_weight['medium'], time['medium'])

    # Tạo và thực hiện hệ thống suy luận mờ
    time_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
    time_simulation = ctrl.ControlSystemSimulation(time_ctrl)
    time_simulation.input['current_weight'] = current_wt
    time_simulation.input['goal_weight'] = goal_wt
    time_simulation.compute()
    return time_simulation.output['time']
def current_calo(gender, weight, height, age, activity_level):
    return caculate_tdee(gender, weight, height, age, activity_level)
def goal_calo(tdee,time_expect,goal_weight,current_weight, calo_consumed):
    calo_per_kg = 7700
    weight_diff = goal_weight - current_weight
    calo_diff = weight_diff*calo_per_kg
    calo_bonus_per_day = calo_diff/time_expect
    calo_goal = calo_bonus_per_day + tdee + calo_consumed
    return calo_goal

def calo_to_goal(request):
    if request.method == 'GET':
        body = request.body.decode('utf-8')
        body_data = json.loads(body)
        time_expert = caculate_time_to_goal(current_wt=body_data.current_wt, goal_wt=body_data.goal_wt)
        tdee = caculate_tdee(body_data.gender,body_data.weight,body_data.height,body_data.age)
        goal_calo = goal_calo(tdee,time_expert,body_data.goal_wt,body_data.current_wt, body_data.calo_consumed)
        return HttpResponse({goal_calo:goal_calo})
