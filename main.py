from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.utils import platform
import requests
import json
import random
from collections import Counter
import os
import certifi
import urllib3

# ========== Android 适配 ==========
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path
    # 请求网络权限
    request_permissions([Permission.INTERNET, Permission.ACCESS_NETWORK_STATE])
    # 使用应用私有存储目录
    CACHE_DIR = app_storage_path()
else:
    CACHE_DIR = os.path.dirname(os.path.abspath(__file__))

# 设置 SSL 证书路径（解决 Android 证书找不到的问题）
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# 禁用 SSL 警告（因为数据源是 HTTP）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SSQ_CACHE = os.path.join(CACHE_DIR, 'ssq_cache.json')
P3_CACHE = os.path.join(CACHE_DIR, 'p3_cache.json')
# ==================================


class LotteryData:
    SSQ_URL = "http://e.17500.cn/getData/ssq.TXT"
    P3_URL = "http://e.17500.cn/getData/pl3.TXT"

    def __init__(self):
        self.ssq_data = []
        self.p3_data = []
        self.load_cache()

    def load_cache(self):
        if os.path.exists(SSQ_CACHE):
            try:
                with open(SSQ_CACHE, 'r') as f:
                    self.ssq_data = json.load(f)
            except:
                pass
        if os.path.exists(P3_CACHE):
            try:
                with open(P3_CACHE, 'r') as f:
                    self.p3_data = json.load(f)
            except:
                pass

    def save_cache(self):
        try:
            with open(SSQ_CACHE, 'w') as f:
                json.dump(self.ssq_data, f)
            with open(P3_CACHE, 'w') as f:
                json.dump(self.p3_data, f)
        except:
            pass

    def fetch_ssq(self):
        try:
            # verify=False 允许 HTTP 明文（Android 9+ 需要）
            resp = requests.get(self.SSQ_URL, timeout=15, verify=False)
            lines = resp.text.strip().splitlines()
            data = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 9:
                    data.append({
                        'issue': parts[0], 'date': parts[1],
                        'r1': int(parts[2]), 'r2': int(parts[3]), 'r3': int(parts[4]),
                        'r4': int(parts[5]), 'r5': int(parts[6]), 'r6': int(parts[7]),
                        'blue': int(parts[8])
                    })
            self.ssq_data = data
            self.save_cache()
            return True, "SSQ: " + str(len(data)) + " periods"
        except Exception as e:
            if self.ssq_data:
                return True, "SSQ cache: " + str(len(self.ssq_data))
            return False, "SSQ failed: " + str(e)

    def fetch_p3(self):
        try:
            resp = requests.get(self.P3_URL, timeout=15, verify=False)
            lines = resp.text.strip().splitlines()
            data = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    data.append({
                        'issue': parts[0], 'date': parts[1],
                        'bai': int(parts[2]), 'shi': int(parts[3]), 'ge': int(parts[4])
                    })
            self.p3_data = data
            self.save_cache()
            return True, "P3: " + str(len(data)) + " periods"
        except Exception as e:
            if self.p3_data:
                return True, "P3 cache: " + str(len(self.p3_data))
            return False, "P3 failed: " + str(e)

    def predict_ssq(self):
        if not self.ssq_data:
            return None
        recent = self.ssq_data[-100:]
        reds = []
        for d in recent:
            reds.extend([d['r1'], d['r2'], d['r3'], d['r4'], d['r5'], d['r6']])
        blues = [d['blue'] for d in recent]
        hot_red = [x[0] for x in Counter(reds).most_common(10)]
        hot_blue = [x[0] for x in Counter(blues).most_common(3)]
        rand_red = sorted(random.sample(range(1, 34), 6))
        rand_blue = random.randint(1, 16)
        hot_pred = sorted(random.sample(hot_red, 6)) if len(hot_red) >= 6 else rand_red
        hot_b = hot_blue[0] if hot_blue else rand_blue
        return {
            'random': (rand_red, rand_blue),
            'hot': (hot_pred, hot_b),
            'latest': self.ssq_data[-1]
        }

    def predict_p3(self):
        if not self.p3_data:
            return None
        recent = self.p3_data[-20:]
        bai = [d['bai'] for d in recent]
        shi = [d['shi'] for d in recent]
        ge = [d['ge'] for d in recent]
        hot_bai = Counter(bai).most_common(1)[0][0] if bai else random.randint(0, 9)
        hot_shi = Counter(shi).most_common(1)[0][0] if shi else random.randint(0, 9)
        hot_ge = Counter(ge).most_common(1)[0][0] if ge else random.randint(0, 9)
        return {
            'random': (random.randint(0,9), random.randint(0,9), random.randint(0,9)),
            'hot': (hot_bai, hot_shi, hot_ge),
            'latest': self.p3_data[-1]
        }


class LotteryApp(App):
    def build(self):
        self.data = LotteryData()
        self.title = 'Lottery Analysis'

        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        title = Label(
            text='Lottery History Analysis',
            font_size='24sp',
            size_hint_y=None,
            height=50,
            color=(1, 0.8, 0, 1)
        )
        root.add_widget(title)

        self.status = Label(
            text='Tap Update to fetch data',
            font_size='14sp',
            size_hint_y=None,
            height=30,
            color=(0.7, 0.7, 0.7, 1)
        )
        root.add_widget(self.status)

        btn_box = GridLayout(cols=3, size_hint_y=None, height=50, spacing=10)
        self.btn_update = Button(text='Update Data', on_press=self.do_update)
        self.btn_ssq = Button(text='SSQ Predict', on_press=self.do_ssq)
        self.btn_p3 = Button(text='P3 Predict', on_press=self.do_p3)
        btn_box.add_widget(self.btn_update)
        btn_box.add_widget(self.btn_ssq)
        btn_box.add_widget(self.btn_p3)
        root.add_widget(btn_box)

        scroll = ScrollView()
        self.result = Label(
            text='Welcome\n\nDisclaimer: Historical data cannot predict lottery.\nReturn rate is ~50%, you will lose long-term.',
            font_size='16sp',
            size_hint_y=None,
            valign='top',
            halign='left',
            text_size=(None, None),
            color=(1, 1, 1, 1)
        )
        self.result.bind(texture_size=self.result.setter('size'))
        scroll.add_widget(self.result)
        root.add_widget(scroll)

        return root

    def do_update(self, instance):
        self.status.text = 'Fetching data...'
        Clock.schedule_once(self._update_data, 0.1)

    def _update_data(self, dt):
        ok1, msg1 = self.data.fetch_ssq()
        ok2, msg2 = self.data.fetch_p3()
        self.status.text = msg1 + ' | ' + msg2
        if ok1 or ok2:
            self.result.text = 'Data updated successfully\n' + msg1 + '\n' + msg2 + '\n\nTap predict buttons to see results'

    def do_ssq(self, instance):
        pred = self.data.predict_ssq()
        if not pred:
            self.result.text = 'Please update data first'
            return
        latest = pred['latest']
        text = (
            "[Shuangseqiu Prediction]\n\n"
            "Latest: " + str(latest['issue']) + " " + str(latest['date']) + "\n"
            "Numbers: " + str(latest['r1']) + " " + str(latest['r2']) + " " + 
            str(latest['r3']) + " " + str(latest['r4']) + " " + 
            str(latest['r5']) + " " + str(latest['r6']) + " + " + 
            str(latest['blue']) + "\n\n"
            "Next prediction:\n"
            "  Random:   " + str(pred['random'][0]) + " + " + str(pred['random'][1]) + "\n"
            "  Hot:      " + str(pred['hot'][0]) + " + " + str(pred['hot'][1]) + "\n\n"
            "Theory:\n"
            "  1st prize: 1/17,721,088\n"
            "  2nd prize: 15/17,721,088\n"
            "  3rd prize: 162/17,721,088\n"
            "  Return rate: ~50%\n\n"
            "Conclusion: All models equal to random"
        )
        self.result.text = text

    def do_p3(self, instance):
        pred = self.data.predict_p3()
        if not pred:
            self.result.text = 'Please update data first'
            return
        latest = pred['latest']
        text = (
            "[Pailie3 Prediction]\n\n"
            "Latest: " + str(latest['issue']) + " " + str(latest['date']) + "\n"
            "Numbers: " + str(latest['bai']) + str(latest['shi']) + str(latest['ge']) + "\n\n"
            "Next prediction:\n"
            "  Random:   " + str(pred['random'][0]) + str(pred['random'][1]) + str(pred['random'][2]) + "\n"
            "  Hot:      " + str(pred['hot'][0]) + str(pred['hot'][1]) + str(pred['hot'][2]) + "\n\n"
            "Theory:\n"
            "  Direct: 1/1000 = 0.1%\n"
            "  Group3: 3/1000 = 0.3%\n"
            "  Group6: 6/1000 = 0.6%\n"
            "  Return rate: ~52%\n\n"
            "Conclusion: History cannot predict random events"
        )
        self.result.text = text


if __name__ == '__main__':
    LotteryApp().run()
