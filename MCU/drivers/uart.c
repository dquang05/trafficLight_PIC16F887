#include <xc.h>
#include <stdio.h>
#include "uart.h"
#include "traffic.h"
#include <string.h>
// Dont have time to makeit more efficient, but it is not a problem for this project
void UART_Init(void) {
    
    TRISCbits.TRISC6 = 0; // TX output
    TRISCbits.TRISC7 = 1; // RX input

    // Baud 9600 @4MHz, BRGH=1
    SPBRG = 25;
    BRG16 = 0;
    BRGH  = 1;

    SYNC = 0;
    SPEN = 1;

    TXEN = 1;
    CREN = 1;

    RCIF = 0;              // clear flag (optional)
    PIE1bits.RCIE = 1;

    PEIE = 1;
    GIE  = 1;
}

// Just write to TXREG, wait for TXIF, done =))
void UART_TxChar(char data) {
    while (!TXIF);    
    TXREG = data;     
}

void UART_TxString(const char* str) {
    while (*str) {
        UART_TxChar(*str++);
    }
}

void UART_TxTrafficState(void) {
    char buffer[40];
    sprintf(buffer, "%d,%d,%d,%d,%d,",
            mode,
            (int)RED1, (int)YELLOW1, (int)GREEN1, countdown_NS);
    sprintf(buffer + strlen(buffer), "%d,%d,%d,%d\n",
            (int)RED2, (int)YELLOW2, (int)GREEN2, countdown_EW);
    UART_TxString(buffer);
}