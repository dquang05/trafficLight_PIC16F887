#include "i2c.h"
/*
I2C driver for PIC16F887, master mode, referenced 
from Microchip's datasheet - page 188-198
Regs:
SPIFF: flag bit, set when transmission/reception is complete
SSPCON: control register 1
    bit 5: SSPEN: 1 to enable I2C, 0 to disable
    bits 3-0: SSPM3..SSPM0: mode select bits, 1000 for I2C Master mode
SSPCON2: control register 2
    bit 0: SEN: Start condition enable bit
    bit 1: RSEN: Repeated start condition enable bit
    bit 2: PEN: Stop condition enable bit
    bit 3: RCEN: Receive enable bit
    bit 4: ACKEN: Acknowledge sequence enable bit
    bit 5: ACKDT: Acknowledge data bit (1 for NACK, 0 for ACK)
SSPSTAT: status register    
    bit 7: SMP: Slew rate control bit (1 for standard speed)
SSPBUF: buffer register for data to be transmitted or received
SSPADD: baud rate generator register, calculated as (Fosc/(4*Fscl))-1 for master mode
PIR1bits.SSPIF: interrupt flag bit, set when transmission/reception is complete 

Steps for master mode:
1. Pullup SCL and SDA lines
2. Configure SSPCON for master mode and enable I2C, wait for SSPIF to clear
Send address:
3. Send slave address with R/W bit in SSPBUF
4. Shift bit to bus: shifft out 8 bits (address + R/W) and wait for SSPIF
5. Check ACK/NACK: MSSP receive ACK form slave: SSPCON2bits.ACKSTAT (0 for ACK, 1 for NACK)
6. End: when 9th bit end, MSSP turn on SSPIF, check ACK/NACK, then master can send next byte or stop condition
Send data:
7. Transmit data: write data to SSPBUF, wait for SSPIF, check ACK/NACK
8. Shift bit to bus: shifft out 8 bits (data) and wait for SSPIF (like step 4)
9. Check ACK/NACK: MSSP receive ACK form slave: SSPCONN2bits.ACKSTAT (0 for ACK, 1 for NACK)
10. SPIFF set when complete (9th bit end), check ACK/NACK, then master can send next byte or stop condition
*/
void i2c_init(void)
{


    TRISCbits.TRISC3 = 1; // SCL input
    TRISCbits.TRISC4 = 1; // SDA input

    SSPCON = 0x28;        // SSPEN=1, I2C Master mode (SSPM=1000)
    SSPCON2 = 0x00;       // Turn off all special features - avoid noise
    SSPSTAT = 0x80;       // SMP=1 (standard speed)

    SSPADD = 9;           // 100kHz @ 4MHz: (Fosc/(4*Fscl))-1 = 9
}

void i2c_start(void) { 
    uint16_t timeout = 10000; // Timeout 10000 cycle
    SSPCON2bits.SEN = 1; 
    while (SSPCON2bits.SEN && timeout) { 
        timeout--; 
    } 
    if (timeout == 0) { 
        SSPCONbits.SSPEN = 0; // Reset I2C 
        SSPCONbits.SSPEN = 1; 
    } 
}

void i2c_stop(void) { 
    uint16_t timeout = 10000; 
    SSPCON2bits.PEN = 1; 
    while (SSPCON2bits.PEN && timeout) { 
        timeout--; 
    } 
    if (timeout == 0) { 
        SSPCONbits.SSPEN = 0; 
        SSPCONbits.SSPEN = 1; 
    } 
}

uint8_t i2c_write(uint8_t u8Data) { 
    uint16_t timeout = 10000; 
    PIR1bits.SSPIF = 0; // clear flag for set again after write
    SSPBUF = u8Data; 
    while (PIR1bits.SSPIF == 0 && timeout) { 
        timeout--; 
    } 
    if (timeout == 0) { // Clear and set it again to reset 
        SSPCONbits.SSPEN = 0; 
        SSPCONbits.SSPEN = 1; 
        return 1; // Error
    } 
    return SSPCON2bits.ACKSTAT; // 
}

uint8_t i2c_read(uint8_t u8Ack) { 
    uint16_t timeout = 10000; 
    uint8_t tmp;
    SSPCON2bits.RCEN = 1; // Enable receive mode
    while (SSPCON2bits.RCEN && timeout) {
        timeout--;
    }
    if (timeout == 0) {
        SSPCONbits.SSPEN = 0;
        SSPCONbits.SSPEN = 1;
        return 0; // Error
    }
    tmp = SSPBUF;
    SSPCON2bits.RCEN = 0; // Clear receive enable bit
    if (u8Ack) {
        SSPCON2bits.ACKDT = 1; // NACK
        SSPCON2bits.ACKDT = 0;
    }

    SSPCON2bits.ACKEN = 1;
    timeout = 10000;
    while (SSPCON2bits.ACKEN && timeout) {
        timeout--;
    }
    if (timeout == 0) {
        SSPCONbits.SSPEN = 0;
        SSPCONbits.SSPEN = 1;
    }

    return tmp;
}

void i2c_repeat_start(void) { 
    uint16_t timeout = 10000; 
    SSPCON2bits.RSEN = 1; 
    while (SSPCON2bits.RSEN && timeout) { 
        timeout--; 
    } 
    if (timeout == 0) { 
        SSPCONbits.SSPEN = 0;
        SSPCONbits.SSPEN = 1; 
    } 
}