from dripline.core import Interface
import time
class Motor:
    ''' This class creates a motor object using dripline commands.'''
    def __init__(self,auths_file,name):
        ''' Initializes a motor object. Connects the motor
            to the dripline interface. Uses functions as described
            in the yaml files for the motors. '''
        self.auths_file = auths_file
        self.name = name
        self.cmd_interface = Interface(dripline_config={'auth-file': self.auths_file})

    def get_name(self):
        ''' Returns the name of the motor. '''
        return self.name

    def get_status(self):
        ''' Returns what status the motor is currently in.
            Status R represents that the motor is not moving and
            ready to accept commands. '''
        command = F"{self.name}_motor_request_status"
        print(command)
        status = self.cmd_interface.get(command).payload.to_python()['value_raw']
        return status

    def wait_for_motor(self):
        ''' Waits for a motor to stop moving and ready to accept a command. '''
        while self.get_status() != 'R':
            print(self.get_status())
            time.sleep(1)

    def move_to_zero(self):
        ''' Moves motor to a calibrated 0 position. '''
        command = F"{self.name}_move_to_position"
        self.cmd_interface.set(command,0)

    def move_steps(self, steps):
        ''' Moves motors a specified number of steps. '''
        command = F"{self.name}_move_steps"
        self.cmd_interface.set(command,steps)

    def set_internal_position_to_value(self, value):
        command = F"{self.name}_set_internal_position"
        self.cmd_interface.set(command, value)

    def stop_and_kill(self):
        ''' Tells motors to stop ASAP. '''
        command = F"{self.name}_status_command"
        self.cmd_interface.set(command, 'stop_and_kill')

# using the classes below is recommended.
class CurvedMirrorMotor(Motor):
    ''' Creates a motor object for the curved mirror.
        Inherits the Motor class and thus has access to all
        its methods. '''
    def __init__(self, auths_file):
        super().__init__(auths_file, 'curved_mirror')

class BottomDielectricPlateMotor(Motor):
    ''' Creates a motor object for the bottom_dielectric_plate.
        Inherits the Motor class and thus has access to all
        its methods. '''
    def __init__(self, auths_file):
        super().__init__(auths_file, 'bottom_dielectric_plate')

class TopDielectricPlateMotor(Motor):
    ''' Creates a motor object for the top_dielectric_plate.
        Inherits the Motor class and thus has access to all
        its methods. '''
    def __init__(self, auths_file):
        super().__init__(auths_file, 'top_dielectric_plate')

class TestMotor(Motor):
    ''' Creates a motor object for the top_dielectric_plate.
        Inherits the Motor class and thus has access to all
        its methods. '''
    def __init__(self, auths_file):
        super().__init__(auths_file, 'resonator_coupling')

class OrpheusMotors:
    ''' Creates Motor objects for Orpheus.
        Takes an auth-file and a list of motors as input.'''
    def __init__(self,auths_file, list_of_motors = []):
        self.auths_file = auths_file
        self.list_of_motors = set(list_of_motors)
        self.motors = []
        for motor in self.list_of_motors:
            if motor == 'curved_mirror':
                self.curved_mirror = CurvedMirrorMotor(self.auths_file)
                self.motors.append(self.curved_mirror)
            elif motor == 'bottom_dielectric_plate':
                self.bottom_plate = BottomDielectricPlateMotor(self.auths_file)
                self.motors.append(self.bottom_plate)
            elif motor == 'top_dielectric_plate':
                self.top_plate = TopDielectricPlateMotor(self.auths_file)
                self.motors.append(self.top_plate)
            else:
                pass
        self.motor_names = [motor.get_name() for motor in self.motors]

    def get_motor_status(self):
        ''' Returns the status of the initialized motors as a list. '''
        status = []
        for motor in self.motors:
            status.append(motor.get_status())
        return status

    def wait_for_motors(self):
        ''' Waits for all the initialized motors to stop moving
            and ready to accept commands. '''
        print(self.motor_names)
        ready = len(self.motor_names)*['R']
        while (self.get_motor_status() != ready):
            print(self.get_motor_status())
            time.sleep(1)
        print('done waiting')

    def move_to_zero(self):
        ''' Moves the motors to 0. '''
        for motor in self.motors:
            motor.move_to_zero()

    def move_by_increment(self, increment_distance,cavity_length_tracker,
                          num_plates, plate_separation):
        ''' Moves initialized motors in a coordinated manner.
            Keeps the dielectric plates even spaced.
            Returns the new resonator length and the new separation
            between the plates.
            All distance/lengths should be in inches.  '''

        cavity_length_tracker = cavity_length_tracker + increment_distance
        new_plate_separation = self.plate_separation(cavity_length_tracker,num_plates)

        if 'curved_mirror' in self.motor_names:
            cm_ind = self.motor_names.index('curved_mirror')
            curved_mirror_steps = self.distance_to_steps(increment_distance)
            print(F'Moving curved mirror motor by {curved_mirror_steps} steps')
            self.motors[cm_ind].move_steps(curved_mirror_steps)

        if 'bottom_dielectric_plate' in self.motor_names:
            bdp_ind = self.motor_names.index('bottom_dielectric_plate')
            diff = plate_separation +increment_distance
            move_bottom_plate = diff - new_plate_separation
            bottom_plate_steps = self.distance_to_steps(move_bottom_plate)
            print(F'Moving bottom plate motor by {bottom_plate_steps} steps')
            self.motors[bdp_ind].move_steps(bottom_plate_steps)

        if 'top_dielectric_plate' in self.motor_names:
            tdp_ind = self.motor_names.index('top_dielectric_plate')
            move_top_plate = new_plate_separation - plate_separation
            top_plate_steps = self.distance_to_steps(move_top_plate)
            print(F'Moving top plate motor by {top_plate_steps} steps')
            self.motors[tdp_ind].move_steps(top_plate_steps)

        return cavity_length_tracker, new_plate_separation

    def stop_and_kill(self):
        for motor in self.motors:
            motor.stop_and_kill()

    def plate_separation(self, length, num_plates):
        ''' Returns the new plate separation between the dielectrics. '''
        return length/(num_plates+1)

    def distance_to_steps(self,distance, pitch = (1/20), steps_per_rotation = 20000):
        ''' Returns the number of steps that a motor needs to
            turn given a distance.Input distance in inches. '''
        num_pitch_lengths = distance/pitch #these many complete rotations
        steps = steps_per_rotation * num_pitch_lengths
        return int(round(steps))

    def set_internal_position_to_value(self, value):
        for motor in self.motors:
            motor.set_internal_position_to_value(value)
