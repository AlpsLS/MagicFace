from datetime import time
from django.db import models


class AttendanceRule(models.Model):
    """考勤规则配置（单例）"""
    checkin_deadline = models.TimeField('签到截止时间', default=time(9, 0, 0),
                                        help_text='此时间之后签到算迟到')
    allow_repeat = models.BooleanField('允许重复签到', default=False,
                                        help_text='同一人同一天是否可重复签到')
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '考勤规则'
        verbose_name_plural = '考勤规则'

    def __str__(self):
        return f'签到截止 {self.checkin_deadline.strftime("%H:%M")}'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={
            'checkin_deadline': time(9, 0, 0),
            'allow_repeat': False,
        })
        return obj


class Person(models.Model):
    """员工/学生，存储人脸 128 维特征向量"""
    name = models.CharField('姓名', max_length=64)
    employee_id = models.CharField('工号/学号', max_length=32, unique=True)
    # 128 维特征向量，JSON 序列化存储
    face_encoding = models.JSONField('人脸特征', null=True, blank=True)
    photo = models.ImageField('照片', upload_to='persons/', null=True, blank=True)
    created_at = models.DateTimeField('录入时间', auto_now_add=True)

    class Meta:
        verbose_name = '人员'
        verbose_name_plural = '人员'

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


class Attendance(models.Model):
    """考勤签到记录"""
    STATUS_CHOICES = [
        ('normal', '正常'),
        ('late', '迟到'),
    ]
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name='签到人员')
    check_in_time = models.DateTimeField('签到时间', auto_now_add=True)
    status = models.CharField('状态', max_length=16, choices=STATUS_CHOICES, default='normal')
    source = models.CharField('来源', max_length=32, default='web_camera')

    class Meta:
        verbose_name = '考勤记录'
        verbose_name_plural = '考勤记录'
        ordering = ['-check_in_time']

    def __str__(self):
        return f"{self.person.name} @ {self.check_in_time}"
