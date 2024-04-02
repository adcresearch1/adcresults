import RPi.GPIO as GPIO
import time
import itertools
import csv
import os
from email import encoders
from github import Github
from github import InputGitTreeElement
import serial

def dac_testing(wr,cslsb_msb):
	GPIO.output(33, 1)	#msb
	GPIO.output(32, 1)
	GPIO.output(23, 1)
	GPIO.output(19, 1)
	GPIO.output(21, 1)
	GPIO.output(24, 1)
	GPIO.output(26, 1)
	GPIO.output(31, 1)
	GPIO.output(29, 1)
	GPIO.output(7, 1)
	GPIO.output(5, 1)
	GPIO.output(3, 1)	#lsb
	GPIO.output(cslsb_msb, 0)
	GPIO.output(wr, 0)
	
def dac_out(binary,wr,cslsb_msb):
	GPIO.output(33, int(binary[0]))	#msb
	GPIO.output(32, int(binary[1]))
	GPIO.output(23, int(binary[2]))
	GPIO.output(19, int(binary[3]))
	GPIO.output(21, int(binary[4]))
	GPIO.output(24, int(binary[5]))
	GPIO.output(26, int(binary[6]))
	GPIO.output(31, int(binary[7]))
	GPIO.output(29, int(binary[8]))
	GPIO.output(7, int(binary[9]))
	GPIO.output(5, int(binary[10]))
	GPIO.output(3, int(binary[11]))	#lsb
	GPIO.output(cslsb_msb, 0)
	GPIO.output(wr, 0)

def adc_in():
	adc_bits = [38,40,15,16,18,22,37,13] #msb to lsb order	

def adc_testing(convst):
	adc_data = []
	adc_bits = [38,40,15,16,18,22,37,13] 	#msb to lsb order
	GPIO.output(convst, 0) 					#falling edge triggers conversion
	GPIO.output(convst, 1)  				#reset convst high
	i = 0
	while i <= 7:
		adc_data.append(GPIO.input(adc_bits[i]))
		i += 1
	return adc_data
	
def bl_to_dec(binary_list): # Converts output of ADC to decimal
    decimal_num = 0
    for bit in binary_list:
        decimal_num = (decimal_num << 1) | bit  # Shift left and bitwise OR with the current bit
    return int(decimal_num)

def send_git():
	g = Github('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')
	repo = g.get_user().get_repo('adcresults')
	file_name = 'testing.py'
	file_path = os.path.join(os.getcwd(),file_name)
	repo.create_file(file_name,'Uploaded from Pi',open(file_path,'rb').read())
	print('CSV file uploaded to adcresults repo')
	
def rpi_to_uno():
	ser = serial.Serial('/dev/serial0', 9600, timeout=1)
	ser.reset_input_buffer()
	message = 'U'
	ser.write(message.encode())
	ser.close()
	
def DAC_cal_mode(wr,cslsb_msb):
	ser = serial.Serial('/dev/serial0', 9600, timeout=1)
	ser.reset_input_buffer()
	for binary in itertools.product([0,1],repeat=12):
		dac_out(binary,wr,cslsb_msb)	#sets dac pins
		message = 'U'
		print('X')
		ser.write(message.encode())
		print('Y')
		while True:
			print('Z')
			response = ser.readline().decode('utf-8').strip()
			print('W')
			if response == 'A':
				break
	message = 'C'
	ser.write(message.encode())
	ser.close()

if __name__ == '__main__':
	GPIO.setmode(GPIO.BOARD)
	outputs = [11,3,5,7,29,31,26,24,21,19,23,32,33,8,10,36,35]
	inputs = [12,38,40,15,16,18,22,37,13]
	for pin in outputs:
		GPIO.setup(pin,GPIO.OUT)
	for pin in inputs:
		GPIO.setup(pin,GPIO.IN)
	wr = 36				
	cslsb_msb = 35			
	convst = 11 			#rpi output
	eoc = 12 				#rpi input
	GPIO.output(convst, 1)  				#set convst high
	#DAC_cal_mode(wr,cslsb_msb)
	with open("dataADC.csv", mode="w") as csvfile:
		fieldnames = ["dac_inputs (V)", "adc_outputs"]
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for binary in itertools.product([0,1],repeat=12):
			dac_out(binary,wr,cslsb_msb)	#sets dac pins
			time.sleep(0.001)
			writer.writerow({"dac_inputs (V)": "{:.6f}".format(2.48*bl_to_dec(binary)/4095), "adc_outputs": bl_to_dec(adc_testing(convst))}) 
			#above reads adc pins and stores data
			time.sleep(0.00001)
	send_git()
	GPIO.cleanup()
	
