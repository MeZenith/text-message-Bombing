# -*- coding: utf-8 -*-
"""接口清单的总入口。

这里不写接口，只是把几个文件里的接口按顺序拼起来，
主程序 import ALL_ENDPOINTS 就能拿到全部 135 条。

想加接口：去对应的文件里加，跟这个文件没关系。
"""

from .app_h5 import ENDPOINTS as APP_H5
from .flow import ENDPOINTS as FLOW
from .insurance import ENDPOINTS as INSURANCE
from .miniapp import ENDPOINTS as MINIAPP

# 顺序跟原来一样：小程序那批 -> App/H5 那批 -> 后补两条 -> 保险那批
ALL_ENDPOINTS = MINIAPP + APP_H5 + FLOW + INSURANCE
