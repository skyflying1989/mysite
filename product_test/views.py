#coding:utf-8
import time, threading, re, socket
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, Http404
from django.core.urlresolvers import reverse
from product_test.models import Terminal, Device, Pool, Task, Subtask, License, Platform, Script
from product_test.form import PoolForm, DeviceForm, TerminalForm, TaskForm, LicenseForm, PlatformForm, ScriptForm, DivErrorList
from product_test.control import TaskThread, telnet
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.core.files.storage import default_storage
from django.db.models.query import QuerySet
from py_compile import compile
# Create your views here.

@login_required
def config(request):
    try:
        pool = Pool.objects.get(user = request.user)
    except Pool.DoesNotExist:
        pool = Pool.objects.create(user = request.user)
    license_list = License.objects.filter(user = request.user)
    return render(request, 'product_test/config.html', {'pool': pool,'license_list':license_list})

@login_required
def pool(request, arg):
    try:
        pool = Pool.objects.get(user = request.user)
    except Pool.DoesNotExist:
        pool = Pool.objects.create(user = request.user) 
    if arg == 'edit':
        if request.method == 'POST':
            form = PoolForm(request.POST)
            if form.is_valid():
                Pool.objects.filter(user = request.user) .update( job = form.cleaned_data['job'].strip(),
                                                                                                 platform=form.cleaned_data['platform'].strip(),
                                                                                                 hw = form.cleaned_data['hw'].strip(),
                                                                                                 image = form.cleaned_data['image'].strip(),
                                                                                                 bootloader = form.cleaned_data['bootloader'].strip(),
                                                                                                 sysloader = form.cleaned_data['sysloader'].strip(),
                                                                                                 cpld = form.cleaned_data['cpld'].strip())
                return HttpResponseRedirect(reverse('product_test:config'))
            else:
                return render(request, 'product_test/pool.html', {'form': form, 'arg':arg})
        elif request.method == 'GET':
            form = PoolForm(initial = {'job':pool.job, 'platform': pool.platform, 'hw':pool.hw, 'image': pool.image, 'bootloader': pool.bootloader, 
                                                       'sysloader': pool.sysloader, 'cpld':pool.cpld}) 
            return render(request, 'product_test/pool.html', {'form': form, 'arg':arg})
    elif arg == 'clear':
        Pool.objects.filter(user = request.user).update(job='', platform='', hw='', image='', bootloader='', sysloader='', cpld='')
        return HttpResponseRedirect(reverse('product_test:config')) 
    else:            
        raise Http404

@login_required
def add_terminal(request):
    if request.method == 'GET':
        form = TerminalForm()
        return  render(request, 'product_test/add_terminal.html', {'form': form}) 
    elif request.method == 'POST':
        form= TerminalForm(request.POST)
        if form.is_valid():
            terminal = Terminal.objects.create(user = request.user,
                                                                       name = form.cleaned_data['name'].strip(),
                                                                       ip = form.cleaned_data['ip'],
                                                                       port = form.cleaned_data['port'])
            for p in xrange(1, terminal.port+1):
                Device.objects.create(sn = '', mac = '', port_id = p, terminal = terminal)      
            return HttpResponseRedirect(reverse('product_test:recent_task'))
        else:
            return render(request, 'product_test/add_terminal.html', {'form': form}) 

@login_required
def operation_terminal(request, index, arg):
    #获取当前terminal并检查异常
    try:
        terminal = Terminal.objects.get(pk = index) 
    except Terminal.DoesNotExist:
        raise Http404     
    #编辑terminal
    if arg == 'edit':
        if request.method == 'GET':
            form = TerminalForm(initial= {'name':terminal.name, 'ip':terminal.ip, 'port':terminal.port})
            return  render(request, 'product_test/edit_terminal.html', {'form': form, 'index':index}) 
        elif request.method == 'POST':
            #先确认terminal下是否有设备处于占用状态
            for device in Device.objects.filter(terminal = terminal):
                if device.state == True:
                    return HttpResponse(u'对不起，终端控制器下有设备正在工作，无法编辑')            
            form = TerminalForm(request.POST)
            if form.is_valid():
                terminal.name = form.cleaned_data['name']
                terminal.ip = form.cleaned_data['ip']
                #根据要设置的port个数调整
                if terminal.port < form.cleaned_data['port']:
                    for p in xrange(terminal.port + 1, form.cleaned_data['port'] + 1):
                        Device.objects.create(sn = '', mac = '', port_id = p, terminal = terminal) 
                    terminal.port = form.cleaned_data['port']
                elif terminal.port > form.cleaned_data['port']:
                    for p in xrange(form.cleaned_data['port'] +1, terminal.port+1):
                        Device.objects.get(port_id = p, terminal = terminal).delete()
                    terminal.port = form.cleaned_data['port']
                terminal.save()
                return HttpResponseRedirect(reverse('product_test:recent_task'))
            else:
                return render(request, 'product_test/edit_terminal.html', {'form': form, 'index':index})            
    #删除terminal
    elif arg == 'delete':
        #先确认terminal下是否有设备处于占用状态
        for device in Device.objects.filter(terminal = terminal):
            if device.state == True:
                return HttpResponse(u'对不起，终端控制器下有设备正在工作，无法删除')
        terminal.delete()
        return HttpResponseRedirect(reverse('product_test:recent_task')) 
    #配置待测设备
    elif arg == 'device_edit':
        if request.method == 'GET':
            initial_list= []
            for device in Device.objects.filter(terminal = terminal).order_by('port_id'):
                initial_list.append({'sn':device.sn, 'mac':device.mac})
            DeviceFormSet = formset_factory(DeviceForm, extra = terminal.port, max_num=terminal.port)
            formset = DeviceFormSet(initial = initial_list)
            i = 0
            for form in formset:
                i = i +1
                form.id = i #标识端口号
                if Device.objects.get(port_id = i, terminal = terminal).state:
                    form.fields['sn'].widget.attrs['readonly'] = True
                    form.fields['sn'].widget.attrs['style'] = 'background-color:#989898' 
                    form.fields['mac'].widget.attrs['readonly'] = True
                    form.fields['mac'].widget.attrs['style'] = 'background-color:#989898'
            return render(request, 'product_test/device.html', {'formset': formset, 'index':index}) 
        elif request.method == 'POST':
            DeviceFormSet = formset_factory(DeviceForm, extra = terminal.port)
            formset = DeviceFormSet(request.POST, error_class=DivErrorList)
            if formset.is_valid():
                #检查是否存在占用的Device
                if len(Device.objects.filter(terminal = terminal, state = True)) != 0:
                    return HttpResponse(u'对不起，有设备正在测试中')
                #检查是否存在重复的SN和MAC
                sn_list = []
                mac_list = []
                for p in formset.cleaned_data:
                    if p['sn'] != '':
                        sn_list.append(p['sn'])
                    if p['mac'] != '':
                        mac_list.append(p['mac'])
                for i in xrange(len(sn_list) -1):
                    if sn_list[i] in sn_list[i+1:]:
                        return HttpResponse(u'对不起，存在重复的设备SN')
                for i in xrange(len(mac_list) -1):
                    if mac_list[i] in mac_list[i+1:]:
                        return HttpResponse(u'对不起，存在重复的设备MAC')
                #更新Device
                for i in xrange(terminal.port):
                    Device.objects.filter(port_id= i+1, terminal = terminal).update(sn = formset.cleaned_data[i]['sn'], mac = formset.cleaned_data[i]['mac'].lower())             
                #更新历史任务
                Task.objects.filter(username = request.user.username, history = False).update(history = True)
                return HttpResponseRedirect(reverse('product_test:recent_task'))
            else:
                i = 0
                for form in formset:
                    i = i +1
                    form.id = i #标识端口号
                    if Device.objects.get(port_id = i, terminal = terminal).state:
                        form.fields['sn'].widget.attrs['readonly'] = True
                        form.fields['sn'].widget.attrs['style'] = 'background-color:#989898' 
                        form.fields['mac'].widget.attrs['readonly'] = True
                        form.fields['mac'].widget.attrs['style'] = 'background-color:#989898'                    
                return render(request, 'product_test/device.html', {'formset': formset, 'index':index})
    
    #清除已保存的device
    elif arg == 'device_clear':
        #检查是否存在占用的Device
        if len(Device.objects.filter(terminal = terminal, state = True)) != 0:
            return HttpResponse(u'对不起，有设备正在测试中')        
        Device.objects.filter(terminal = Terminal.objects.get(pk = index)).update(mac = '', sn = '') 
        Task.objects.filter(username = request.user.username, history = False).update(history = True)
        return HttpResponseRedirect(reverse('product_test:operation_terminal', args=(index, 'device_edit')))
    
    #抛出页面不存在
    else:
        raise Http404    
     
   
@login_required
def task(request):
    task_list = Task.objects.order_by('-begin')
    name = request.GET.get('name', '') 
    if name != '':
        task_list = task_list.filter(name__contains = name)
        name = '&name='+name
    username = request.GET.get('username', '') 
    if username != '':       
        task_list = task_list.filter(username__contains = username)
        username = '&username='+username
    sn = request.GET.get('sn', '') 
    if sn != '':
        task_list = task_list.filter(subtask__sn__contains = sn)
        sn = '&sn='+sn
    task_num = len(task_list)
    total_page_num = (task_num+10-1)/10
    query = name + username +sn
    if request.GET.get('page', '') != '':
        page_num = int(request.GET['page'])
    else:
        page_num = 1
    if page_num == 1:
        flag1 = 1
    else:
        flag1 = 0
    if  page_num*10 >= task_num:
        task_list = task_list[(page_num-1)*10:]
        flag2 = 1
    else:
        task_list = task_list[(page_num-1)*10 : page_num*10 ] 
        flag2 = 0
    return render(request, 'product_test/task.html', {'task_list': task_list, 'page_num': page_num, 
                                                                                      'task_num':task_num, 'flag1':flag1, 'flag2':flag2,
                                                                                      'query' : query, 'total_page_num':total_page_num}) 
       
        
@login_required
def operation_task(request, index, arg):
    #获取当前任务并检查异常
    try:
        task = Task.objects.get(pk = index)
    except Task.DoesNotExist:
        raise Http404
    #删除任务
    if arg == 'delete':
        if not request.user.has_perm('product_test.delete_task'):
            return HttpResponse(u'对不起，你没有权限操作') 
        task.delete() 
        query = "?"
        for i  in request.GET:
            query = query + i +"=%s&" % request.GET[i]
        return HttpResponseRedirect(reverse('product_test:task')+query) 
    
    #停止任务
    elif arg == 'stop':
        rc = 1
        for thread in threading.enumerate():
            if thread.getName() == 'task-%s' % index:
                thread.stop()
                thread.join()
                rc = 0
                break
        #异常情况下的处理
        if rc:
            Task.objects.filter(pk=index).update(state = 4)
            subtask_list = Task.objects.get(pk=index).subtask_set.all()
            for subtask in subtask_list:
                Device.objects.filter(sn = subtask.sn).update(state=False)         
        return HttpResponseRedirect(reverse('product_test:recent_task'))
    
    #抛出页面不存在
    else:
        raise Http404


@login_required    
def perform_task(request):
    #获取pool信息
    pool = Pool.objects.get(user = request.user)
    if pool.platform == '':
        return HttpResponse(u'对不起，平台及版本信息不能为空')     
    #获取device信息, 检查可用device, 检查terminal IP
    device_queryset = []
    for terminal in Terminal.objects.filter(user = request.user):
        device_list = Device.objects.filter(terminal = terminal, sn__regex=r'[0-9]+', mac__regex=r'[A-Fa-f0-9]+', state = False).order_by('port_id')
        length = len(device_list)
        if length % 2 !=0 or length == 0 :
            return HttpResponse(u'对不起，终端控制器%s的可用设备个数必须是偶数且不为0, 目前可用设备个数为%d' % (terminal.name, length)) 
        try:
            connect = telnet(terminal.ip, timeout = 7)
            connect.close()
        except:
            return HttpResponse(u'对不起，终端控制器%s无法连接, 请检查网络连接' % terminal.name)
        device_queryset.append(device_list)      
    #之前的任务置为历史任务
    Task.objects.filter(username = request.user.username, history = False).update(history = True) 
    #创建任务
    task = Task.objects.create(name = pool.job, username = request.user.username,
                                                  platform = pool.platform, hw = pool.hw, image = pool.image, 
                                                  bootloader = pool.bootloader, sysloader = pool.sysloader, 
                                                  cpld = pool.cpld, 
                                                  begin = time.strftime('%Y-%m-%d %X', time.localtime()))
    #占用device并创建子任务, 子任务状态更新为"初始化"
    for device_list  in device_queryset:
        for device in device_list:
            #device.state = True
            device.save()
            Subtask.objects.create( task = task, terminal = device.terminal.name, ip = device.terminal.ip, 
                                                     port_id = device.port_id, sn = device.sn, mac = device.mac, state = 1) 
    
    #调用任务线程开始测试
    TaskThread('task-%s' % task.pk, task.pk).start()
    return HttpResponseRedirect(reverse('product_test:recent_task'))     

@login_required
def recent_task(request):
    tasklist= Task.objects.filter(username=request.user.username, history = False)
    terminal_list = Terminal.objects.filter(user = request.user)
    if len(tasklist):
        subtasklist=Subtask.objects.filter(task = tasklist[0])
        flag = True
        return render(request, 'product_test/recent_task.html', {'subtasklist':subtasklist, 'terminal_list':terminal_list, 'flag':flag, 'task':tasklist[0]})
    else:
        flag = False
        return render(request, 'product_test/recent_task.html', {'terminal_list':terminal_list, 'flag':flag})
    
@login_required
def subtask(request, index):
    #获取subtask list并检查异常
    try:
        subtask_list = Task.objects.get(pk = index).subtask_set.all()
    except Task.DoesNotExist:
        raise Http404
    return render(request, 'product_test/subtask.html', {'subtask_list': subtask_list, 'index': index})

@login_required
def operation_subtask(request, index1, index2, arg):
    #获取当前subtask并检查异常
    try:
        subtask = Task.objects.get(pk = index1).subtask_set.get(pk = index2)
    except Task.DoesNotExist:
        raise Http404 
    except Subtask.DoesNotExist:
        raise Http404
    #查看结果详情
    if arg == 'log':            
        return  render(request, 'product_test/log.html', {'loglist':subtask.log.split('\n'), 'subtask':subtask, 'index':index1})
    elif arg == 'consolelog':
        return  render(request, 'product_test/console_log.html', {'console_log':subtask.console_log}) 
    else:
        raise Http404
        
@login_required
def license(request, arg):
    if arg == 'add':
        if request.method == 'GET':
            form = LicenseForm()
            return render(request, 'product_test/license.html', {'form':form, 'arg':arg})
        elif request.method == 'POST':
            form = LicenseForm(request.POST)
            if form.is_valid():
                for name in form.cleaned_data['name']:
                    License.objects.create(user = request.user, name = name, deadline = form.cleaned_data['deadline'], username = form.cleaned_data['username'].strip())
                return HttpResponseRedirect(reverse('product_test:config'))
            else:
                return render(request, 'product_test/license.html', {'form':form, 'arg':arg})
    elif arg == 'clear':
        License.objects.filter(user = request.user).delete()
        return HttpResponseRedirect(reverse('product_test:config'))
    elif re.search(r'^(delete)/(\d+)$', arg) != None:
        p = re.search(r'^(delete)/(\d+)$', arg) 
        #检查license是否存在
        try:
            license = License.objects.get(pk = p.group(2))
        except:
            raise Http404
        #编辑license
        if p.group(1) == 'delete':
            license.delete()
            return HttpResponseRedirect(reverse('product_test:config'))
    else:
        raise Http404

@login_required
def manage(request):
    #判断权限
    if not request.user.has_perm('product_test.delete_task'):
        return HttpResponse(u'对不起，你没有权限操作')
    platform_list = Platform.objects.all().order_by('name')
    name = request.GET.get('platform_name', '') 
    if name != '':
        platform_list = platform_list.filter(name__contains = name)
        name = '&platform_name='+name
    platform_num = len(platform_list)
    total_page_num = (platform_num+5-1)/5
    query = name
    if request.GET.get('page', '') != '':
        page_num = int(request.GET['page'])
    else:
        page_num = 1
    if page_num == 1:
        flag1 = 1
    else:
        flag1 = 0
    if  page_num*5 >= platform_num:
        platform_list = platform_list[(page_num-1)*5:]
        flag2 = 1
    else:
        platform_list = platform_list[(page_num-1)*5 : page_num*5 ] 
        flag2 = 0    
    script_list = Script.objects.all()
    return render(request, 'product_test/manage.html', {'platform_list': platform_list, 'script_list': script_list, 'page_num': page_num, 
                                                                                             'platform_num':platform_num, 'flag1':flag1, 'flag2':flag2,
                                                                                             'query' : query, 'total_page_num':total_page_num})

@login_required
def platform(request, arg):
    #判断权限
    if not request.user.has_perm('product_test.delete_task'):
        return HttpResponse(u'对不起，你没有权限操作')    
    #添加平台
    if arg == 'add':
        if request.method == 'POST':
            form = PlatformForm(request.POST)
            if form.is_valid():
                Platform.objects.create(name = form.cleaned_data['name'], memory = form.cleaned_data['memory'],
                                                         script = form.cleaned_data['script'])
                return HttpResponseRedirect(reverse('product_test:manage'))
            else:
                return render(request, 'product_test/platform.html', {'form':form, 'arg':arg})
        elif request.method == 'GET':
            form = PlatformForm()
            return render(request, 'product_test/platform.html', {'form':form, 'arg':arg})
    elif re.search(r'^(edit|delete)/(\d+)$', arg) != None:
        p = re.search(r'^(edit|delete)/(\d+)$', arg) 
        #检查平台是否存在
        try:
            platform = Platform.objects.get(pk = p.group(2))
        except:
            raise Http404        
         #编辑平台
        if p.group(1) == 'edit':
            if request.method == 'POST':
                form = PlatformForm(request.POST)
                if form.is_valid():
                    platform.name = form.cleaned_data['name']
                    platform.memory = form.cleaned_data['memory']
                    platform.script = form.cleaned_data['script']
                    platform.save()
                    return HttpResponseRedirect(reverse('product_test:manage'))
                else:
                    return render(request, 'product_test/platform.html', {'form':form, 'arg':arg})
            elif request.method == 'GET':
                form = PlatformForm(initial = {'name':platform.name, 'memory':platform.memory, 'script':platform.script.pk})
                return render(request, 'product_test/platform.html', {'form':form, 'arg':arg})            
         #删除平台
        elif p.group(1) == 'delete':
            platform.delete()
            return HttpResponseRedirect(reverse('product_test:manage'))
    else:
        raise Http404
  
@login_required      
def script(request, arg):
    #判断权限
    if not request.user.has_perm('product_test.delete_task'):
        return HttpResponse(u'对不起，你没有权限操作')    
    #添加脚本
    if arg == 'add':
        if request.method == 'POST':
            form = ScriptForm(request.POST, request.FILES)
            if form.is_valid():
                script = Script.objects.create(files = form.cleaned_data['files'], username = request.user.username)
                path = default_storage.path(script.files.name)
                compile(path)
                return HttpResponseRedirect(reverse('product_test:manage'))
            else:
                return render(request, 'product_test/script.html', {'form':form, 'arg':arg})
        elif request.method == 'GET':
            form = ScriptForm()
            return render(request, 'product_test/script.html', {'form':form, 'arg':arg})
    elif re.search(r'^(edit|delete)/(\d+)$', arg) != None:
        p = re.search(r'^(edit|delete)/(\d+)$', arg) 
        #检查脚本是否存在
        try:
            script = Script.objects.get(pk = p.group(2))
        except:
            raise Http404
        #删除脚本
        if p.group(1) == 'delete': 
            if len(Platform.objects.filter(script = script)) !=0:
                return HttpResponse('删除失败, 原因: 已有平台关联该脚本，')
            else:
                default_storage.delete(script.files.name)
                default_storage.delete(script.files.name+'c')
                script.delete()
            return HttpResponseRedirect(reverse('product_test:manage'))
    else:
        raise Http404
        