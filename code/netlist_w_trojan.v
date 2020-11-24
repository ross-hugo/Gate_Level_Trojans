----------------------------------------
Trojan Template
----------------------------------------

wire R1, R2, R3, R4, R5, R6, R7, victim_x, Trigger_out1

and AND2_TR0(R1,I1,I2);

and AND2_TR1(R2,I3,I4);

and AND2_TR2(R3,I5,I6);

and AND2_TR3(R4,I7,I8);

and AND2_TR4(R5,R1,R2);

and AND2_TR5(R6,R3,R4);

and AND2_TR6(Trigger_out1,R5,R6);

XOR AND2_PL0(victim_x,Trigger_out1, victim);
----------------------------------------
Design Before Trojan Insertion
----------------------------------------

module dff (clk,Q,D);
	output Q;
	input D;
	input clk;
	reg Q=0;

	always @(posedge clk)
	begin
		Q = D;
	end
endmodule

module s27(GND,VDD,CK,G0,G1,G17,G2,G3);
	input GND,VDD,CK,G0,G1,G2,G3;
	output G17;

		wire G5,G10,G6,G11,G7,G13,G14,G8,G15,G12,G16,G9;

		dff DFF_0(CK,G5,G10);
		dff DFF_1(CK,G6,G11);
		dff DFF_2(CK,G7,G13);
		not NOT_0(G14,G0);
		not NOT_1(G17,G11);
		and AND2_0(G8,G14,G6);
		or OR2_0(G15,G12,G8);
		or OR2_1(G16,G3,G8);
		nand NAND2_0(G9,G16,G15);
		nor NOR2_0(G10,G14,G11);
		nor NOR2_1(G11,G5,G9);
		nor NOR2_2(G12,G1,G7);
		nor NOR2_3(G13,G2,G12);

endmodule

----------------------------------------
Nets G11,G10,G8,G12,G14,G0,VDD,GND Activates the Trojan (i.e. trigger nets) 
and Net G5 is impacted by the payload (victim)
----------------------------------------
module dff (clk,Q,D);
	output Q;
	input D;
	input clk;
	reg Q=0;

	always @(posedge clk)
	begin
		Q = D;
	end
endmodule

module s27(GND,VDD,CK,G0,G1,G17,G2,G3);

	input GND,VDD,CK,G0,G1,G2,G3;
	output G17;

		wire G5,G10,G6,G11,G7,G13,G14,G8,G15,G12,G16,G9;

		wire R4, R5, R6, R1, R2, R3, Trigger_out1, I8, I1, I3, I2, I5, I4, I7, I6, G5_x;

		dff DFF_0(CK,G5_x,G10);
		dff DFF_1(CK,G6,G11);
		dff DFF_2(CK,G7,G13);
		not NOT_0(G14,G0);
		not NOT_1(G17,G11);
		and AND2_0(G8,G14,G6);
		or OR2_0(G15,G12,G8);
		or OR2_1(G16,G3,G8);
		nand NAND2_0(G9,G16,G15);
		nor NOR2_0(G10,G14,G11);
		nor NOR2_1(G11,G5_x,G9);
		nor NOR2_2(G12,G1,G7);
		nor NOR2_3(G13,G2,G12);

	assign I8= G11;
	assign I1= G10;
	assign I3= G8;
	assign I2= G12;
	assign I5= G14;
	assign I4= G0;
	assign I7= VDD;
	assign I6= GND;

		and AND2_TR0(R1,I1,I2);
		and AND2_TR1(R2,I3,I4);
		and AND2_TR2(R3,I5,I6);
		and AND2_TR3(R4,I7,I8);
		and AND2_TR4(R5,R1,R2);
		and AND2_TR5(R6,R3,R4);
		and AND2_TR6(Trigger_out1,R5,R6);
		XOR AND2_PL0(G5,Trigger_out1, G5_x);
endmodule
