import time
import math
from machine import Pin, I2C

ADDR  = (0X53)

LTR390_MAIN_CTRL = (0x00)  # Main control register
LTR390_MEAS_RATE = (0x04)  # Resolution and data rate
LTR390_GAIN = (0x05)  # ALS and UVS gain range
LTR390_PART_ID = (0x06)  # Part id/revision register
LTR390_MAIN_STATUS = (0x07)  # Main status register
LTR390_ALSDATA = (0x0D)  # ALS data lowest byte, 3 byte
LTR390_UVSDATA = (0x10)  # UVS data lowest byte, 3 byte
LTR390_INT_CFG = (0x19)  # Interrupt configuration
LTR390_INT_PST = (0x1A)  # Interrupt persistance config
LTR390_THRESH_UP = (0x21)  # Upper threshold, low byte, 3 byte
LTR390_THRESH_LOW = (0x24)  # Lower threshold, low byte, 3 byte

#ALS/UVS measurement resolution, Gain setting, measurement rate
RESOLUTION_20BIT_TIME400MS = (0X00)
RESOLUTION_19BIT_TIME200MS = (0X10)
RESOLUTION_18BIT_TIME100MS = (0X20)#default
RESOLUTION_17BIT_TIME50MS  = (0x3)
RESOLUTION_16BIT_TIME25MS  = (0x40)
RESOLUTION_13BIT_TIME12_5MS  = (0x50)
RATE_25MS = (0x0)
RATE_50MS = (0x1)
RATE_100MS = (0x2)# default
RATE_200MS = (0x3)
RATE_500MS = (0x4)
RATE_1000MS = (0x5)
RATE_2000MS = (0x6)

# measurement Gain Range.
GAIN_1  = (0x0)
GAIN_3  = (0x1)# default
GAIN_6 = (0x2)
GAIN_9 = (0x3)
GAIN_18 = (0x4)


class LTR390:
    def __init__(self, address=ADDR):
        self.i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=100000)
        self.address = address

        self.ID = self.Read_Byte(LTR390_PART_ID)
        # print("ID = %#x" %self.ID)
        if(self.ID != 0xB2):
            print("read ID error!,Check the hardware...")
            return
        self.Write_Byte(0x00, 0x02) # MAIN_CTRL=UVS in Active Mode
        self.Write_Byte(0x01, 0x36) 
        self.Write_Byte(0x02, 0x8) 
        self.Write_Byte(0x03, 0x45) 
        self.Write_Byte(0x04, 0x22)
        self.Write_Byte(0x05, 0x1)
        # self.Write_Byte(0x06, 0xb2)
        # self.Write_Byte(0x07, 0x18)
        self.Write_Byte(0x19, 0x14)  #LTR390_INT_CFG
        self.Write_Byte(0x21, 0x20) # 288 max
        self.Write_Byte(0x22, 1)
        self.Write_Byte(0x23, 0)
        self.Write_Byte(0x24, 5)   # 5 min
        self.Write_Byte(0x25, 0)
        self.Write_Byte(0x26, 0)
        
        
    def Read_Byte(self, cmd):
        rdate = self.i2c.readfrom_mem(int(self.address), int(cmd), 1)
        return rdate[0]

    def Write_Byte(self, cmd, val):
        self.i2c.writeto_mem(int(self.address), int(cmd), bytes([int(val)]))
    def UVS(self):
        # self.Write_Byte(LTR390_MAIN_CTRL, 0x0A) #  UVS in Active Mode
        Data1 = self.Read_Byte(LTR390_UVSDATA)
        Data2 = self.Read_Byte(LTR390_UVSDATA + 1)
        Data3 = self.Read_Byte(LTR390_UVSDATA + 2)
        uv =  (Data3 << 16)| (Data2 << 8) | Data1
        # UVS = Data3*65536+Data2*256+Data1
        # print("UVS = ", UVS)
        return uv
    def ALS(self):
        # self.Write_Byte(LTR390_MAIN_CTRL, 0x02) #  UVS in Active Mode
        Data1 = self.Read_Byte(LTR390_ALSDATA)
        Data2 = self.Read_Byte(LTR390_ALSDATA + 1)
        Data3 = self.Read_Byte(LTR390_ALSDATA + 2)
        als =  (Data3 << 16)| (Data2 << 8) | Data1
        return als
if __name__ == '__main__':
	sensor = LTR390()
	time.sleep(1)
	try:
		while True:
			UVS = sensor.ALS()
			print("UVS: %d" %UVS)
			time.sleep(0.5)
			
	except KeyboardInterrupt:
		# sensor.Disable()
		exit()






