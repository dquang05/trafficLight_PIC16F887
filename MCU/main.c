#include <xc.h>
#include "pic16f887.h"
#include "pic16f887_bsp.h"
#include "traffic.h"
#include "lcd.h"
#include "uart.h"
#include <string.h>

volatile uint8_t tick_500ms = 0;
volatile uint8_t last_mode = 0xFF;
volatile uint8_t rb0_pending = 0;
volatile uint8_t rb1_pending = 0;
volatile uint8_t rb2_pending = 0;

volatile uint8_t rb1_armed = 1;
volatile uint8_t rb2_armed = 1;

volatile uint8_t portb_last = 0xFF;

volatile char uart_cmd_buffer[8];
volatile uint8_t uart_cmd_ready = 0;
volatile uint8_t uart_tx_pending = 0;

static void System_Init(void);
static void Interrupt_Init(void);
static void Process_Uart_Command(const char *cmd);
static void Copy_Uart_Command(char *dst, uint8_t dst_size);

void System_Init(void)
{
    ANSEL = 0;
    ANSELH = 0;

    TRISA = 0x00;
    PORTA = 0x00;

    TRISBbits.TRISB0 = 1;
    TRISBbits.TRISB1 = 1;
    TRISBbits.TRISB2 = 1;

    OPTION_REGbits.nRBPU = 0;
    WPUBbits.WPUB0 = 1;
    WPUBbits.WPUB1 = 1;
    WPUBbits.WPUB2 = 1;

    PORTB = 0x00;

    TRISC = 0x00;
    PORTC = 0x00;
    TRISE = 0x00;

    TRISCbits.TRISC3 = 1;
    TRISCbits.TRISC4 = 1;

    RED1 = 0;
    GREEN1 = 0;
    YELLOW1 = 0;
    RED2 = 0;
    GREEN2 = 0;
    YELLOW2 = 0;
}

void Interrupt_Init(void)
{
    INTCONbits.GIE = 0;
    INTCONbits.PEIE = 0;

    INTCONbits.INTE = 0;
    INTCONbits.INTF = 0;
    OPTION_REGbits.INTEDG = 0;

    IOCBbits.IOCB1 = 1;
    IOCBbits.IOCB2 = 1;

    portb_last = PORTB;
    INTCONbits.RBIF = 0;
    INTCONbits.RBIE = 1;

    T1CON = 0b00110001;
    TMR1 = 3036;
    PIR1bits.TMR1IF = 0;
    PIE1bits.TMR1IE = 1;

    INTCONbits.PEIE = 1;
    INTCONbits.GIE = 1;
    INTCONbits.INTE = 1;
}

static void Process_Uart_Command(const char *cmd)
{
    if (strcmp(cmd, "M") == 0)
    {
        mode = (mode + 1) % 3;
        exitsign = 1;
        timer_counter = 0;
    }
    else if (strcmp(cmd, "A") == 0)
    {
        mode = 0;
        exitsign = 1;
        timer_counter = 0;
    }
    else if (strcmp(cmd, "N") == 0)
    {
        mode = 1;
        exitsign = 1;
        timer_counter = 0;
    }
    else if (strcmp(cmd, "F") == 0)
    {
        mode = 2;
        exitsign = 1;
        timer_counter = 0;
    }
    else if (mode == 1)
    {
        if (strcmp(cmd, "R1") == 0)
        {
            road1_flag = 1;
        }
        else if (strcmp(cmd, "R2") == 0)
        {
            road2_flag = 1;
        }
    }
}

static void Copy_Uart_Command(char *dst, uint8_t dst_size)
{
    uint8_t i;

    INTCONbits.GIE = 0;
    for (i = 0; i < dst_size - 1; i++)
    {
        dst[i] = uart_cmd_buffer[i];
        if (dst[i] == '\0')
        {
            break;
        }
    }
    dst[dst_size - 1] = '\0';
    uart_cmd_ready = 0;
    INTCONbits.GIE = 1;
}

void __interrupt() ISR(void)
{
    if (PIR1bits.RCIF)
    {
        static char rx_buffer[8];
        static uint8_t rx_index = 0;
        char data;

        if (RCSTAbits.OERR)
        {
            RCSTAbits.CREN = 0;
            RCSTAbits.CREN = 1;
            rx_index = 0;
        }

        if (RCSTAbits.FERR)
        {
            char dummy = RCREG;
            (void)dummy;
            rx_index = 0;
        }
        else
        {
            data = RCREG;

            if (data < 32 && data != '\n')
            {
                rx_index = 0;
            }
            else if (data == '\n')
            {
                rx_buffer[rx_index] = '\0';

                if (!uart_cmd_ready)
                {
                    uint8_t i;
                    for (i = 0; i < sizeof(uart_cmd_buffer); i++)
                    {
                        uart_cmd_buffer[i] = rx_buffer[i];
                        if (rx_buffer[i] == '\0')
                            break;
                    }
                    uart_cmd_buffer[sizeof(uart_cmd_buffer) - 1] = '\0';
                    uart_cmd_ready = 1;
                }

                rx_index = 0;
            }
            else if (rx_index < sizeof(rx_buffer) - 1)
            {
                rx_buffer[rx_index++] = data;
            }
            else
            {
                rx_index = 0;
            }
        }
    }

    if (INTCONbits.INTF)
    {
        INTCONbits.INTF = 0;
        rb0_pending = 1;
    }

    if (INTCONbits.RBIF)
    {
        uint8_t now = PORTB;

        if ((portb_last & (1 << 1)) && !(now & (1 << 1)))
        {
            if (rb1_armed)
            {
                rb1_pending = 1;
                rb1_armed = 0;
            }
        }
        else if (!(portb_last & (1 << 1)) && (now & (1 << 1)))
        {
            rb1_armed = 1;
        }

        if ((portb_last & (1 << 2)) && !(now & (1 << 2)))
        {
            if (rb2_armed)
            {
                rb2_pending = 1;
                rb2_armed = 0;
            }
        }
        else if (!(portb_last & (1 << 2)) && (now & (1 << 2)))
        {
            rb2_armed = 1;
        }

        portb_last = now;
        INTCONbits.RBIF = 0;
    }

    if (PIR1bits.TMR1IF)
    {
        PIR1bits.TMR1IF = 0;
        TMR1 = 3036;

        uart_tx_pending = 1;

        tick_500ms++;
        if (tick_500ms >= 2)
        {
            tick_500ms = 0;
            timer_counter++;
        }
    }
}

int main(void)
{
    char cmd[8];

    System_Init();

    mode = 0;
    last_mode = 0xFF;
    timer_counter = 0;
    exitsign = 1;
    system_state = 0;
    tick_500ms = 0;
    uart_cmd_ready = 0;
    uart_tx_pending = 1;

    I2C_LCD_Init();
    Interrupt_Init();
    UART_Init();

    while (1)
    {
        if (rb0_pending)
        {
            rb0_pending = 0;
            mode = (mode + 1) % 3;
            exitsign = 1;
            timer_counter = 0;
            uart_tx_pending = 1;
        }

        if (rb1_pending)
        {
            rb1_pending = 0;

            if (mode == 1)
            {
                __delay_ms(20);

                if (PORTBbits.RB1 == 0)
                {
                    road1_flag = 1;
                    road2_flag = 0;
                    exitsign = 1;
                    timer_counter = 0;
                    uart_tx_pending = 1;
                }
            }
        }

        if (rb2_pending)
        {
            rb2_pending = 0;

            if (mode == 1)
            {
                __delay_ms(20);

                if (PORTBbits.RB2 == 0)
                {
                    road2_flag = 1;
                    road1_flag = 0;
                    exitsign = 1;
                    timer_counter = 0;
                    uart_tx_pending = 1;
                }
            }
        }

        if (uart_cmd_ready)
        {
            Copy_Uart_Command(cmd, sizeof(cmd));
            Process_Uart_Command(cmd);
            uart_tx_pending = 1;
        }

        if (last_mode != mode)
        {
            RED1 = 0;
            GREEN1 = 0;
            YELLOW1 = 1;
            YELLOW2 = 1;

            Opposite_State();
            I2C_LCD_Clear();
            I2C_LCD_BackLight(1);

            switch (mode)
            {
            case 0:
                I2C_LCD_Puts("MODE_AUTO");
                break;
            case 1:
                I2C_LCD_Puts("MODE_MANUAL");
                break;
            case 2:
                I2C_LCD_Puts("MODE_FLASHING");
                break;
            }

            last_mode = mode;
        }

        switch (mode)
        {
        case 0:
            Auto_Mode_Timer();
            break;

        case 1:
            Manual_Mode();
            break;

        case 2:
            Midnight_Mode_Timer();
            break;
        }

        if (uart_tx_pending)
        {
            uart_tx_pending = 0;
            UART_TxTrafficState();
        }
    }
}