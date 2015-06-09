#coding:utf-8
from django import forms
from product_test.models import  Device, Pool, Platform,Terminal, Script
from django.forms.util import ErrorList
import re


class DivErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()
    def as_divs(self):
        if not self: return u''
        return u''.join([u'%s' % e for e in self])

class PoolForm(forms.Form):
    def __init__(self, *args, **kwargs):
            super(PoolForm, self).__init__(*args, **kwargs)       
            choice_platform = []
            for p in Platform.objects.order_by('name'):
                choice_platform.append((p.name, p.name))
            self.fields['job'] = forms.CharField(max_length = 40, label=u'工单号')
            self.fields['platform'] = forms.ChoiceField(choices= choice_platform, label=u'平台名称')
            self.fields['hw'] = forms.CharField(max_length = 4, label=u'硬件版本号')
            self.fields['image'] =  forms.CharField(max_length = 40, label=u'OS image版本')
            self.fields['bootloader'] = forms.CharField(max_length = 40, label=u'Bootloader版本')
            self.fields['sysloader'] = forms.CharField(max_length = 40, label=u'Sysloader版本') 
            self.fields['cpld'] = forms.CharField(required=False, max_length = 10, label=u'CPLD版本')
            
                
class DeviceForm(forms.Form):
    sn = forms.CharField(required = False,
                                         max_length =16, 
                                         min_length =16, 
                                         label=u'SN号', 
                                         widget = forms.TextInput(attrs={'onkeypress' : 'return handleEnter(this, event)'}))
    mac = forms.CharField(required = False,
                                            max_length =12, 
                                             min_length = 12, 
                                            label=u'MAC地址', 
                                            widget = forms.TextInput(attrs={'onkeypress' : 'return handleEnter(this, event)'}))
    def clean_sn(self):
        data = self.cleaned_data['sn']
        if data != '':
            if re.search('^\d+$', data) == None:
                raise forms.ValidationError(u'SN只包含数字')
        return data
    
    def clean_mac(self):
        data = self.cleaned_data['mac']
        if data != '':
            if re.search('^[a-fA-F0-9]+$', data) == None:
                raise forms.ValidationError(u'MAC地址必须是a~f(或A~F)和0~9组成的字符串')
        return data
    
    def clean(self):
        cleaned_data = super(DeviceForm, self).clean()
        sn = cleaned_data.get('sn')
        mac = cleaned_data.get('mac')
        if sn != '':
            if mac == '':
                self._errors["mac"] = self.error_class([u'当SN不为空时，MAC为必填项'])
                #del cleaned_data["mac"]
        else:
            if mac != '':
                self._errors["sn"] = self.error_class([u'当MAC不为空时，SN为必填项'])
                #del cleaned_data["sn"]
        return cleaned_data
        

class TerminalForm(forms.Form):
    name = forms.CharField(max_length =35, label=u'名称')
    ip = forms.IPAddressField(label=u'IP地址')
    port = forms.IntegerField(min_value= 1, label=u'端口个数') 


class TaskForm(forms.Form):
    name = forms.CharField(max_length=30, label=u'名字')
    def __init__(self, user, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)       
        terminal_choice = []
        terminal_list = Terminal.objects.filter(user = user)
        for terminal in terminal_list:
            terminal_choice.append((terminal.name, terminal.name))
        self.fields['terminal'] = forms.MultipleChoiceField(choices= terminal_choice, 
                                                    widget=forms.CheckboxSelectMultiple, 
                                                    label=u'选择终端控制器',
                                                    )

class LicenseForm(forms.Form):    
    choices = [('plat', 'platform-base license'),
                       ('plat-trial', 'platform-trial license'),
                       ('av', 'anti-virus feature license'),
                       ('ips', 'ips feature license'),
                       ('urld', 'url db feature license'),
                       ('appd', 'app db feature license'),
                       ('qos', 'qos feature license'),
                       ('qos-trial', 'qos-trial license'),
                       ('sess', 'session license'),
                       ('perf', 'performance enhancement license'), 
                       ('feat', 'feature-trial license'),
                       ('thre', 'threat feature license'),
                       ('thre-trial', 'threat-trial license'),
                       ('inte', 'intelligence feature license'),
                       ('inte-trial', 'intelligence-trial license'),                    
                       ('nbc', 'nbc feature license'),
                       ('scvp', 'secure connect license'),
                       ('vsys', 'virtual system license')
                       ]
    name = forms.MultipleChoiceField(choices = choices,label=u'选择许可证',
                                                                widget=forms.SelectMultiple(attrs={'style': 'height:150px'}),
                                                                ) 
    username = forms.CharField(max_length= 35, label=u'客户名称', required = False)
    deadline = forms.CharField(max_length = 10, label=u'截止日期/时长', required = False,
                                                    help_text =u'截止日期是YYYY-MM-DD的格式，时长是不大于3位数的数字')
    
    def clean_deadline(self):
        data = self.cleaned_data['deadline']
        if data != '':
            if re.search('^\d{1,3}$', data) == None and re.search('^\d{4}-\d{2}-\d{2}$', data) == None:
                raise forms.ValidationError(u'截止日期/时长格式不正确')
        return data 

class PlatformForm(forms.Form):
    name = forms.CharField(max_length = 30, label=u'平台名称')
    memory = forms.CharField(max_length = 30, label=u"内存大小", help_text = u'请输入单位为KB的内存大小，可参考show memory的total大小')
    script = forms.ModelChoiceField(queryset=Script.objects.all(), label=u'测试脚本', required= False)


class ScriptForm(forms.Form):
    files = forms.FileField(label=u'上传脚本')
    
    
    