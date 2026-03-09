from django.db import models


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
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name='签到人员')
    check_in_time = models.DateTimeField('签到时间', auto_now_add=True)
    source = models.CharField('来源', max_length=32, default='web_camera')

    class Meta:
        verbose_name = '考勤记录'
        verbose_name_plural = '考勤记录'
        ordering = ['-check_in_time']

    def __str__(self):
        return f"{self.person.name} @ {self.check_in_time}"
