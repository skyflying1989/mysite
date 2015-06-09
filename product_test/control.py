#coding:utf-8
import telnetlib, threading, socket, time, re,os, traceback
from product_test.models import  Platform, Device, Terminal, Task, Subtask, License
from django.conf import settings 
from django.contrib.auth.models import User


class telnet(telnetlib.Telnet):
    def __init__(self, ip = None, port = 0, timeout = 0, pk= -1):
        self.pk = pk
        self.args = {}
        if timeout:
            telnetlib.Telnet.__init__(self, ip, port, timeout)
        else:
            telnetlib.Telnet.__init__(self, ip, port)
    def sendcmd(self, send_str, expect_list, timeout = 7, flag = 1):
        if flag:
            self.write('%s\r' % send_str)
        else:
            self.write('%s' % send_str)
        if timeout == 0:
            result = self.expect(expect_list)
        else:
            result = self.expect(expect_list, timeout)
        if self.pk >= 0:
            subtask = Subtask.objects.get(pk = self.pk)
            subtask.console_log = subtask.console_log + result[2].decode('utf-8')
            subtask.save()
        return result
    def waitfor(self, expect_list, timeout = 300):
        if timeout == 0:
            result = self.expect(expect_list)
        else:
            result = self.expect(expect_list, timeout)
        if self.pk >= 0:
            subtask = Subtask.objects.get(pk = self.pk)
            subtask.console_log = subtask.console_log + result[2].decode('utf-8')
            subtask.save() 
        return result
    def log(self, strings, code):
        if self.pk >= 0:
            subtask = Subtask.objects.get(pk = self.pk)
            strings = strings.decode('utf-8')
            if code == 0 :
                subtask.log = subtask.log + time.strftime('%Y-%m-%d %X', time.localtime()) + "  [FAIL]%s\n"  % strings + "-------------------------------------------------------------------------\n" 
            elif code == 1:
                subtask.log = subtask.log + time.strftime('%Y-%m-%d %X', time.localtime()) + "  [SUCCESS]%s\n"  % strings + "-------------------------------------------------------------------------\n" 
            elif code == 2:
                subtask.log = subtask.log + time.strftime('%Y-%m-%d %X', time.localtime()) + "  [ERROR]%s\n"  % strings
            elif code == 3:
                subtask.log = subtask.log + time.strftime('%Y-%m-%d %X', time.localtime()) + "  [INFO] %s\n"  % strings
            subtask.save() 
    def prompt(self, strings):
        if self.pk >= 0:
            Subtask.objects.filter(pk = self.pk).update(prompt = strings) 

        
class SubtaskThread (threading.Thread):   
    def __init__(self, **args): 
        threading.Thread.__init__(self)
        self.pk = args['pk']
        self.queue = args['queue']
        self.ping_signal = args['ping_signal']
        self.dut = telnet(pk = self.pk)
        subtask = Subtask.objects.get(pk =self.pk)
        self.dut.args['sn'] = subtask.sn
        self.dut.args['mac'] = subtask.mac[0:4] + '.' + subtask.mac[4:8] + '.' + subtask.mac[8:12]
        self.dut.args['platform'] = args['platform']
        self.dut.args['hw'] = args['hw']
        self.dut.args['image'] = args['image']
        self.dut.args['bootloader'] = args['bootloader']
        self.dut.args['sysloader'] = args['sysloader']
        self.dut.args['license'] = args['license']
        self.dut.args['memory'] = args['memory']
        self.dut.args['cpld'] = args['cpld']
    def run(self):
        #初始化"错误"标志位
        error = 0
        #获取IP地址和端口号
        subtask = Subtask.objects.get(pk =self.pk)
        ip = subtask.ip
        port = subtask.port_id 
        
        #更新子任务运行状态为"正在运行"
        Subtask.objects.filter(pk = self.pk).update(state = 2)
        
        #登陆测试设备
        self.dut.log('登陆测试设备,(端口:%d, SN:%s)' % (port, self.dut.args['sn'].encode('utf-8')), 3)
        try:                 
            self.dut.open(ip, port+2000)
            j = 0
            while j<3:
                result = self.dut.sendcmd('', ['login','#'])
                if result[0] != -1:
                    break
                j = j + 1
            if j == 3:
                self.dut.log('设备没有响应: 1、检查串口线是否插紧 2、检查串口波特率是否匹配',2)
                #"错误"标志位置位
                error = 1
            else:
                if result[0] == 0:
                    if 'SG-6000' in self.dut.args['platform']:
                        self.dut.sendcmd('hillstone', ['password'])
                        self.dut.sendcmd('hillstone', ['#'], timeout = 20)
                    else:
                        self.dut.sendcmd('admin', ['password'])
                        self.dut.sendcmd('admin', ['#'], timeout = 20)                        
                else:
                    self.dut.sendcmd('end', ['#'])                      
        except :
            self.dut.log('发生异常:\n%s' % traceback.format_exc(), 2) 
            #"错误"标志位置位
            error = 1
       
        #登陆测试设备失败
        if error:
            self.dut.log('登陆测试设备,(端口:%d, SN:%s)' % (port, self.dut.args['sn'].encode('utf-8')), 0)
            #事件信号全部置位，防止hang住情况出现
            for m in self.ping_signal:
                m.set() 
            #"结果"标志位置位
            rc = 0

        #登陆测试设备成功，开始执行测试
        else:  
            self.dut.log('连接测试设备,(端口:%d, SN:%s)' % (port, self.dut.args['sn'].encode('utf-8')), 1)
            try: 
                #获取跟平台关联的测试脚本
                path = Platform.objects.get(name = self.dut.args['platform']).script.files.name
                scriptname = re.search('script/(\S+).py', path).group(1)
                exec('from media.product_test.script.%s import %s' % (scriptname, scriptname)) 
                #开始执行测试脚本
                exec('rc = %s(self.dut, queue=self.queue, ping_signal=self.ping_signal)' % scriptname) 
            except :
                self.dut.log('发生异常:\n%s' % traceback.format_exc(), 2) 
                #事件信号全部置位，防止hang住情况出现
                for m in self.ping_signal:
                    m.set()
                #"结果"标志位置位
                rc = 0
            
        #测试结束，断开连接
        self.dut.close()            
            
        #根据结果更新子任务运行状态为"已结束", 更新运行结果
        if rc:
            Subtask.objects.filter(pk=self.pk).update(state=3, result=1) 
            f = open(settings.MEDIA_ROOT + r'/product_test/record/(%s)()().txt' % self.dut.args['sn'] , 'w')
            f.write('sucess!!!!')
            f.close()                
        else:
            Subtask.objects.filter(pk=self.pk).update(state=3, result=2)
            
    def stop(self):
        self.dut.close()
            

class TaskThread (threading.Thread):   
    def __init__(self, threadname, pk):
        threading.Thread.__init__(self, name=threadname)
        self.pk = pk
    def run(self):
        #更新任务状态为"初始化", 此时不能停止任务
        Task.objects.filter(pk= self.pk).update(state = 1)
        #置"停止"标志位
        self.Flag = True
        
        #获取任务相关信息        
        task = Task.objects.get(pk = self.pk) 
        tmp = re.search(r'\d+.\d+.\d+', task.bootloader)
        if tmp:
            bootloader =  'Bootloader ' + tmp.group(0)
        else:
            bootloader = task.bootloader
        tmp = re.search(r'\d+.\d+.\d+', task.sysloader)
        if tmp:
            sysloader = 'Sysloader ' + tmp.group(0)
        else:
            sysloader = task.sysloader
        license = {}
        for p in License.objects.filter(user = User.objects.get(username = task.username)):
            license[p.name.encode('utf-8')] = (p.username.encode('utf-8'), p.deadline) 
        memory = Platform.objects.get(name = task.platform).memory
        
        # 获取子任务
        thread_list = []
        subtask_list = Subtask.objects.filter(task__pk = self.pk)
        
        #清理terminal端口:
        ip1 = ''
        terminal = None
        for subtask in subtask_list:
            try:
                ip2 = subtask.ip
                if ip2 != ip1:
                    if terminal:
                        terminal.close() 
                    terminal = telnet(ip2)
                    terminal.sendcmd('',['Password\n'])
                    terminal.sendcmd('cisco', ['>'])
                    terminal.sendcmd('en', ['Password'])
                    terminal.sendcmd('cisco', ['#'])             
                for i in xrange(0,3):
                    terminal.sendcmd('clear line %d' % subtask.port_id, ['[confirm]']) 
                    terminal.sendcmd('', ['#'])
                ip1 = ip2
            except:
                Subtask.objects.filter(pk=subtask.pk).update(log=u' [INFO] 清除terminal端口异常\n')
                
        #调用子任务线程
        for i in xrange(0, len(subtask_list), 2):
            signal_group = (threading.Event(), threading.Event(), threading.Event())  #定义事件信号
            for j in xrange(i,i+2):
                thread = SubtaskThread(pk = subtask_list[j].pk, queue = j, ping_signal = signal_group,
                                                         platform =  task.platform, hw = task.hw, image = task.image,
                                                         bootloader = bootloader, sysloader = sysloader, 
                                                         license = license, memory = memory, cpld = task.cpld)
                thread_list.append(thread)
                thread.start()
        
        #更新任务状态为"正在运行"，此时可以停止任务
        Task.objects.filter(pk= self.pk).update(state = 2)
        
        #监视子线程运行情况
        length = len(thread_list)
        while self.Flag:
            #if  not len([ thread for thread in thread_list if thread.isAlive()]):
                #break
            m = length
            for thread in thread_list:
                if thread.isAlive():
                    break
                else:
                    m = m -1
            if not m:
                break
            time.sleep(2)
        
        #任务完成，更新任务运行状态为"已结束"，更新结束时间和运行结果，更新设备占用情况
        if self.Flag:                        
            if len(Subtask.objects.filter(result = 2, task = Task.objects.get(pk = self.pk))) :
                Task.objects.filter(pk = self.pk).update(result = 2, state = 3, over = time.strftime('%Y-%m-%d %X', time.localtime())) 
            else:
                Task.objects.filter(pk = self.pk).update(result = 1, state = 3, over = time.strftime('%Y-%m-%d %X', time.localtime()))
            for subtask in subtask_list:
                Device.objects.filter(sn = subtask.sn).update(state=False)            
        
        #任务被终止
        else:
            for thread in thread_list:
                thread.stop()
                thread.join()
            Task.objects.filter(pk= self.pk).update(state = 4, over = time.strftime('%Y-%m-%d %X', time.localtime()))
            for subtask in subtask_list:
                Device.objects.filter(sn = subtask.sn).update(state=False)             
        
    def stop(self):
        self.Flag = False

