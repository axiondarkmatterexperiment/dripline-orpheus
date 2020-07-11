from dripline.core import Interface
import time
class Motor:
    def __init__(self,auths_file,name):
        self.auths_file = auths_file
        self.name = name
        self.cmd_interface = Interface(dripline_config={'auth-file': self._auths_file})

    def get_status(self):
        command = F"{self.name}_motor_request_status"
        status = self.cmd_interface.get(command).payload.to_python()['value_raw']
        return status

    def move_to_zero(self):
        command = F"{self.name}_move_to_position"
        self.cmd_interface.set(command,0)

    def move_steps(self, steps):
        command = F"{self.name}_move_steps"
        self.cmd_interface.set(command,steps)

class CurvedMirrorMotor(Motor):
    def __init__(self, auths_file):
        super().__init__(auths_file, 'curved_mirror')

class BottomDielectricPlateMotor(Motor):
    def __init__(self, auths_file):
        super().__init__(auths_file, 'bottom_dielectric_plate')

class TopDielectricPlateMotor(Motor):
    def __init__(self, auths_file):
        super().__init__(auths_file, 'top_dielectric_plate')

class OrpheusMotors:
    def __init__(self,auths_file):
        self.auths_file = auths_file
        self.curved_mirror = CurvedMirrorMotor(self.auths_file)
        self.bottom_plate = BottomDielectricPlateMotor(self.auths_file)
        self.top_plate = TopDielectricPlateMotor(self.auths_file)

    def curved_mirror(self):
        return self.curved_mirror

    def bottom_plate(self):
        return self.bottom_plate

    def top_plate(self):
        return self.top_plate

    def get_motor_status(self):
        curved_mirror_status = self.curved_mirror.get_status()
        bottom_plate_status = self.bottom_plate.get_status()
        top_plate_status = self.top_plate.get_status()
        return [curved_mirror_status, bottom_plate_status, top_plate_status]

    def wait_for_motors(self):
        while (get_motor_status() != ['R','R','R']):
            print(get_motor_status())
            time.sleep(1)
        print('done waiting')

    def move_to_zero(self):
        self.curved_mirror.move_to_zero()
        self.bottom_plate.move_to_zero()
        self.top_plate.move_to_zero()
