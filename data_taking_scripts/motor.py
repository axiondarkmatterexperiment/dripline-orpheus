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
        status = self.cmd_interface.get(command).payload.to_python()['value_raw']
        return status

    def wait_for_motor(self):
        ''' Waits for a motor to stop moving and ready to accept a command. '''
        while get_status() != 'R':
            print(get_status())
            time.sleep(1)

    def move_to_zero(self):
        ''' Moves motor to a calibrated 0 position. '''
        command = F"{self.name}_move_to_position"
        self.cmd_interface.set(command,0)

    def move_steps(self, steps):
        ''' Moves motors a specified number of steps. '''
        command = F"{self.name}_move_steps"
        self.cmd_interface.set(command,steps)

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

class OrpheusMotors:
    ''' Creates Motor objects for Orpheus as a whole. '''
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
        ''' Returns the status of all 3 motors as a list. '''
        curved_mirror_status = self.curved_mirror.get_status()
        bottom_plate_status = self.bottom_plate.get_status()
        top_plate_status = self.top_plate.get_status()
        return [curved_mirror_status, bottom_plate_status, top_plate_status]

    def wait_for_motors(self):
        ''' Waits for all three motors to stop moving and ready to
            accept commands. '''
        while (self.get_motor_status() != ['R','R','R']):
            print(self.get_motor_status())
            time.sleep(1)
        print('done waiting')

    def move_to_zero(self):
        ''' Moves all three motors to 0. '''
        self.curved_mirror.move_to_zero()
        self.bottom_plate.move_to_zero()
        self.top_plate.move_to_zero()

    def move_by_increment(self, increment_distance, dielectric_plate_thickness,
                          cavity_length_tracker, num_plates, initial_plate_separation):
        ''' Moves all three motor in a coordinated manner.
            Keeps the dielectric plates even spaced.
            Returns the new resonator length and the new separation
            between the plates. '''

        curved_mirror_steps = self.curved_mirror_distance_to_steps(increment_distance)
        print(F'Moving curved mirror motor by {curved_mirror_steps} steps')
        self.curved_mirror.move_steps(curved_mirror_steps)
        #adjusting bottom dielectric plate
        cavity_length_tracker = cavity_length_tracker + increment_distance
        new_plate_separation = self.plate_separation(cavity_length_tracker,num_plates)
        diff = initial_plate_separation +increment_distance
        move_bottom_plate = diff - new_plate_separation
        bottom_plate_steps = self.plates_distance_to_steps(move_bottom_plate,dielectric_plate_thickness)
        print(F'Moving bottom plate motor by {bottom_plate_steps} steps')
        self.bottom_plate.move_steps(bottom_plate_steps)
        #adjusting top dielectric plate
        move_top_plate = new_plate_separation - initial_plate_separation
        top_plate_steps = self.plates_distance_to_steps(move_top_plate,dielectric_plate_thickness)
        print(F'Moving top plate motor by {top_plate_steps} steps')
        self.top_plate.move_steps(top_plate_steps)
        return cavity_length_tracker, new_plate_separation

    def plate_separation(self, length, num_plates):
        ''' Returns the new plate separation between the dielectrics. '''
        return length/(num_plates+1)

    def plates_distance_to_steps(self,distance,plate_thickness,holder_thickness = (1/4),
                                 lip_thickness = (1/20),pitch=(1/20),
                                 steps_per_rotation = 20000):
        ''' Returns the number of steps to move the alumina holders
            based on the distance teh plates need to move. Takes plate_thickness
            and the distance as input and returns an integer as output. '''
        holder_center = holder_thickness/2
        plate_center = lip_thickness + plate_thickness/2
        gap = holder_center - plate_center
        actual_distance = distance + gap
        num_pitch_lengths = actual_distance/pitch #these many complete rotations
        steps = steps_per_rotation * num_pitch_lengths
        return int(round(steps))

    def curved_mirror_distance_to_steps(self,distance, pitch = (1/20), steps_per_rotation = 20000):
        ''' Returns the number of steps that curved mirror needs to move based on the
            distance. '''
        num_pitch_lengths = distance/pitch #these many complete rotations
        steps = steps_per_rotation * num_pitch_lengths
        return int(round(steps))
