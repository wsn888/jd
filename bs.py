import requests

import random

number2 = random.randint(9857,9857)

dict = {
        '账号':'密码'
        }

* 使用说明：
* 使用前，手机注册小米运动账号，设置第三方接入，然后到网页提交步数即可
* 隐私说明：本站保障您的隐私安全，请勿设置和其他软件同样密码，建议简单密码即可
* 注意不要使用小米账号登录，使用手机号重新注册，可以和小米一个手机号，是两个独立的系统

    'User_Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)',

}

for key in dict:

    number,password = (key,dict[key])

    lj = f"http://42.193.130.93:8080/mi?phoneNumber={number}&password={password}&steps={number2}"

    r = requests.get(url = lj,headers=header)

    r.encoding = r.apparent_encoding

    t = r.text.encode('gbk', 'ignore').decode('gbk')

    print(t)

    print("您今日运动步数结果为{}".format(number2))
