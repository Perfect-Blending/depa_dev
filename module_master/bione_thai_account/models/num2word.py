# -*- coding: utf-8 -*-
currency={
    "th_TH":{
        "name":"บาท",
        "partial":"สตางค์",
        "end":"ถ้วน",
    },
    #FIXME: don't know how to use for the other lang
    "en_US":{
        "name":"BAHT",
        "partial":"STANG",
        "end":"ONLY",
    }
}

sym={
    "en_US": {
        "sep": " ",
        "0": "ZERO",
        "x": ["ONE","TWO","THREE","FOUR","FIVE" ,"SIX","SEVEN","EIGHT","NINE"],
        "1x": ["TEN","ELEVEN","TWELVE","THIRTEEN","FOURTEEN","FIFTEEN","SIXTEEN","SEVENTEEN","EIGHTEEN","NINETEEN"],
        "x0": ["TWENTY","THIRTY","FOURTY","FIFTY","SIXTY","SEVENTY","EIGHTY","NINETY"],
        "100": "HUNDRED",
        "1K": "THOUSAND",
        "1M": "MILLION",
    },
    "th_TH": {
        "sep": "",
        "0": "ศูนย์",
        "x": ["หนึ่ง","สอง","สาม","สี่","ห้า" ,"หก","เจ็ด","แปด","เก้า"],
        "x0": ["สิบ","ยี่สิบ","สามสิบ","สี่สิบ","ห้าสิบ","หกสิบ","เจ็ดสิบ","แปดสิบ","เก้าสิบ"],
        "x1": "เอ็ด",
        "100": "ร้อย",
        "1K": "พัน",
        "10K": "หมื่น",
        "100K": "แสน",
        "1M":"ล้าน",
    }
}


def _num2word(n,l="en_US"):
    if n==0:
        return sym[l]["0"] + ""
    elif n<10:
        return sym[l]["x"][n-1]
    elif n<100:
        if l=="en_US":
            if n<20:
                return sym[l]["1x"][n-10]
            else:
                return sym[l]["x0"][int(n/10-2)]+(int(n%10) and sym[l]["sep"]+_num2word(int(n%10),l) or "")
        elif l=="th_TH":
            return sym[l]["x0"][int(n/10-1)]+(int(n%10) and (int(n%10)==1 and sym[l]["x1"] or sym[l]["x"][int(n%10-1)]) or "")
    elif n<1000:
        return sym[l]["x"][int(n/100-1)]+sym[l]["sep"]+sym[l]["100"]+(int(n%100) and sym[l]["sep"]+_num2word(int(n%100),l) or "")

    elif n<1000000:
        if l=="en_US":
            return _num2word(int(n/1000),l)+sym[l]["sep"]+sym[l]["1K"]+(int(n%1000) and sym[l]["sep"]+_num2word(int(n%1000),l) or "")
        elif l=="th_TH":
            if n<10000:
                return sym[l]["x"][int(n/1000-1)]+sym[l]["1K"]+(int(n%1000) and _num2word(int(n%1000),l) or "")
            elif n<100000:
                return sym[l]["x"][int(n/10000-1)]+sym[l]["10K"]+(int(n%10000) and _num2word(int(n%10000),l) or "")
            else:
                return sym[l]["x"][int(n/100000-1)]+sym[l]["100K"]+(int(n%100000) and _num2word(int(n%100000),l) or "")
    elif n<1000000000:
        return _num2word(int(n/1000000),l)+sym[l]["sep"]+sym[l]["1M"]+sym[l]["sep"]+(int(n%1000000) and _num2word(int(n%1000000),l) or "")
    else:
        return "N/A"

def num2word(n,l="th_TH"):
    base=0
    end=0
    number = n
    if type(n) == type(''):
        number=float(n)
    word = ''
    if type(number) in (type(0),type(0.0)):
        number = ('%.2f'%number).split('.')
        base = _num2word(int(number[0]),l=l)
        if int(number[1])!=0:
            end = _num2word(int(number[1]),l=l)
        if base!=0 and end==0:
            word=base\
                +sym[l]['sep']\
                +currency[l]['name']\
                +sym[l]['sep']\
                +currency[l]['end']
        if base!=0 and end!=0:
            word=base+currency[l]['name']+end+currency[l]['partial']
    return word


