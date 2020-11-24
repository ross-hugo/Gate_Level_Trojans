wire R1, R2, R3, R4, R5, R6, R7, victim_x, Trigger_out1

and AND2_TR0(R1,I1,I2);

and AND2_TR1(R2,I3,I4);

and AND2_TR2(R3,I5,I6);

and AND2_TR3(R4,I7,I8);

and AND2_TR4(R5,R1,R2);

and AND2_TR5(R6,R3,R4);

and AND2_TR6(Trigger_out1,R5,R6);

XOR AND2_PL0(victim_x,Trigger_out1, victim);
