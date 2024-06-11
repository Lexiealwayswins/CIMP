from django.http import JsonResponse

# 运用可变参数
# 当 ensure_ascii 参数设置为 False 时，生成的 JSON 字符串将保留非 ASCII 字符，
# 而不会进行转义。这在需要包含非 ASCII 字符的情况下是非常有用的，
# 比如需要保留特殊字符、表情符号等
def JR(data, **karg):
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False}, safe=False, **karg)