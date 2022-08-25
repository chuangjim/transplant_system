from my_serial import ReqResSerial
import time

class MT24X_Exception(Exception):
    pass

class MT24X_E1_Exception(Exception):
    pass

class MT24X_E2_Exception(Exception):
    pass

class MT24X(ReqResSerial):
    def __init__(self, acc_step, dec_step, vec_step, port, baudrate, ratio=1.8195,terminator = "\r\n"):
        super().__init__(
            port = port, baudrate = baudrate, terminator = terminator)
        self.ratio = ratio
        self.acc_step = acc_step
        self.dec_step = dec_step
        self.vec_step = vec_step
        self.block_size = [5, 8]
        self.block_step = [3111, 1934]
        self.block_count = 0
        self.block_init_pos = [35771, 44881]
        # self.block_init_pos = [22800, 37600]
        self.frame_init_pos = []
        self.plate_size = [8, 12]
        self.plate_limit = [35000, 0]
        self.plate_init_pos = [45400, 47970]
        self.calibration_pos = [41228, 48519]
        self.niddle_center_pos = [1112, 594]
        self.plate_step = [1800, 1806]
        self.transplate_init_pos = [23465, 90000]
        self.z_pos = -27900
        self.w_pick_pos = -3970
        self.w_place_pos = -3300
        self.w_safe_pos = -2000

    def request(self, cmd, timeout = None, retry_times = 0, return_value=False):
        resp = super().request(cmd, timeout, retry_times)
        resp = resp.replace(self._terminator, "") if resp is not None else "no response"

        result = f"{cmd} <- {resp}"
        if return_value :
            print(result)

        if "E1" in resp:
            raise MT24X_E1_Exception("Error code: E1 ({})".format(cmd))
            return False
        elif "E2" in resp:
            raise MT24X_E2_Exception("Error code: E2 ({})".format(cmd))
            return False
        elif "K" in resp:
            return True
        elif resp.lstrip('-').isdigit():
            return int(resp)
        # else:
        #     raise MT24X_Exception("Parsing response fail! ({})".format(resp))
    
    def check(self):
        return self.request('CHECK', timeout = 2, retry_times = 5)

    def get_zero(self, m_id):
        return self.request("GET_ZERO {}".format(m_id))

    def get_run(self, m_id):
        return self.request("GET_RUN {}".format(m_id), timeout = 0.5)
        # return self.request("GET_RUN {}".format(m_id), timeout = 0.5, return_value=True)

    def get_in(self, x, timeout = 0.5, retry_times = 3):
        cmd = "GET_IN {}".format(x)
        v = self.request(cmd, timeout, retry_times)
        return v

    def get_pos(self, x, timeout = 0.5, retry_times = 3):
        cmd = "GET_POS {}".format(x)
        v = self.request(cmd, timeout, retry_times, return_value = True)
        return v
    
    def get_p(self, x, timeout = 0.5, retry_times = 3):
        cmd = "GET_P {}".format(x)
        v = self.request(cmd, timeout, retry_times, return_value = True)
        return v        

    def set_out(self, y, v, timeout = 0.5, retry_times = 3):
        cmd = "SET_OUT {} {}".format(y, v)
        v = self.request(cmd, timeout, retry_times, return_value = True)
        return v

    def get_out(self, y, timeout = 0.5, retry_times = 3):
        cmd = "GET_OUT {}".format(y)
        v = self.request(cmd, timeout, retry_times)
        return v

    def check_pos(self, m_id, pos):
        pos_before = -100000000
        while True:
            pos_now = self.get_p(m_id) 
            # print("pos_before:", pos_before, "pos_now:", pos_now)
            if pos_now == pos:
                break
            if pos_before == pos_now:
                # print("can't move")
                break
            else:
                # print("pos:", pos_now)
                pos_before = pos_now
                time.sleep(0.1)

    def wait(self):
        while True:
            # print(self.get_run(3))
            if not self.get_run(0) and not self.get_run(1) and not self.get_run(2) and not self.get_run(3):
                break
            time.sleep(0.1)

    def calibration(self, m_id, acc_step=None, dec_step=None, vec_step=None, wait=False):
        if not acc_step: acc_step = self.acc_step
        if not dec_step: dec_step = self.dec_step
        if not vec_step: vec_step = self.vec_step
        self.request(
            "MODE_H {} 0".format(m_id),
            timeout=0.5, retry_times = 2)
        self.request(
            "H_ACC_DEC {} {} {}".format(m_id, acc_step, dec_step),
            timeout=0.5, retry_times = 2)
        self.request(
            "H_V {} {}".format(m_id, vec_step),
            timeout=0.5, retry_times = 2)
        if wait:
            self.wait()
        # self.check_pos(m_id, 0)

    def move_MODE_P_REL(self, m_id, delta_step, acc_step=None, dec_step=None, vec_step=None, wait = False):
        if not acc_step: acc_step = self.acc_step
        if not dec_step: dec_step = self.dec_step
        if not vec_step: vec_step = self.vec_step
        self.request(
            "MODE_P {} 0".format(m_id),
            timeout=0.5, retry_times = 2)
        self.request(
            "P_ACC_DEC_V {} {} {} {}".format(
                m_id, acc_step, dec_step, vec_step), 
            timeout=0.5, retry_times = 2)
        self.request(
            "P_REL {} {}".format(m_id, delta_step), 
            timeout=0.5, retry_times = 2, return_value = True)
        if wait:
            self.wait()

    def move_MODE_P(self, m_id, step, acc_step=None, dec_step=None, vec_step=None, wait=False):
        if not acc_step: acc_step = self.acc_step
        if not dec_step: dec_step = self.dec_step
        if not vec_step: vec_step = self.vec_step
        self.request(
            "MODE_P {} 0".format(m_id),
            timeout=0.5, retry_times = 2)
        self.request(
            "P_ACC_DEC_V {} {} {} {}".format(
                m_id, acc_step, dec_step, vec_step), 
            timeout=0.5, retry_times = 2)
        self.request(
            "P_ABS {} {}".format(m_id, step), 
            timeout=0.5, retry_times = 2, return_value = True)
        if wait:
            self.wait()
            # self.check_pos(m_id, step)

    def move_MODE_L(self, m_ids, step, acc_step=None, dec_step=None, vec_step=None):
        if not acc_step: acc_step = self.acc_step
        if not dec_step: dec_step = self.dec_step
        if not vec_step: vec_step = self.vec_step
        m_ids_str = " ".join([str(x)for x in m_ids])
        step_str = " ".join([str(x)for x in step])
        self.request(
            "L_ACC_DEC_V 0 {} {} {}".format(
                acc_step, dec_step, vec_step), 
            timeout=0.5, retry_times = 2)
        self.request(
            "L_ABS 0 {} {}".format(m_ids_str, step_str), 
            timeout=0.5, retry_times = 2, return_value = True)
        self.wait()

    def move_MODE_L_REL(self, m_ids, delta_step, acc_step=None, dec_step=None, vec_step=None):
        if not acc_step: acc_step = self.acc_step
        if not dec_step: dec_step = self.dec_step
        if not vec_step: vec_step = self.vec_step        
        m_ids_str = " ".join([str(x)for x in m_ids])
        step_str = " ".join([str(x)for x in delta_step])
        self.request(
            "L_ACC_DEC_V 0 {} {} {}".format(
                acc_step, dec_step, vec_step), 
            timeout=0.5, retry_times = 2)
        self.request(
            "L_REL 0 {} {}".format(m_ids_str, step_str), 
            timeout=0.5, retry_times = 2, return_value = True)
        self.wait()
    def move_to_center(self, point):
        x_diff = int((self.niddle_center_pos[0] - point[0])*self.ratio)
        y_diff = int((self.niddle_center_pos[1] - point[1])*self.ratio)
        # self.move_MODE_L([0, 1], 3000, 3000, 1000, [x_diff + x_center, y_diff + y_center])
        self.move_MODE_P_REL(0, x_diff)
        self.move_MODE_P_REL(1, y_diff, wait=True)

    def get_hole_pos(self, egg_count):
        hole_0 = self.plate_init_pos[0]+int((egg_count//self.plate_size[1])*self.plate_step[0])
        hole_1 = self.plate_init_pos[1]-int((egg_count%self.plate_size[1])*self.plate_step[1])
        return hole_0, hole_1