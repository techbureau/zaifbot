from json import dumps


def save_order_log(order_result):
    f = open('./order_history.log', 'a')
    order_result_str = dumps(order_result)
    f.write(order_result_str + '\n')
    f.close()
