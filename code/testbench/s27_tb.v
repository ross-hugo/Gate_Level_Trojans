// Testbench
module test;
//module s27(GND,VDD,CK,G0,G1,G17,G2,G3);
  reg  CK, GND,VDD,G0,G1,G2,G3; //assign inputs as reg
  wire G17;                          //assign outputs as wire
  
  //create array for text file
  // [3:0] = 4 bit data
    // [0:5] = 6 rows  in the file input_data.txt
    reg[3:0] read_data [0:5];
  // Instantiate device under test
  s27 s27_0(.CK(CK),
          .GND(GND),
		  .VDD(VDD),
		  .G0(G0),
		  .G1(G1),
		  .G17(G17),
		  .G2(G2),
		  .G3(G3));
    integer i;
	
	 initial begin
   

    CK = 0;
	GND=0;
	VDD=1; //VDD is always 1
	G0= 0;
	G1= 0;
	G2= 0;
	G3= 0;

	end 
	
	always 
	#1000 CK<=~CK;
	
	
	initial
    begin 
        // readmemb = read the binary values from the file
        // other option is 'readmemh' for reading hex values
        // create Modelsim project to use relative path with respect to project directory
        $readmemb("C:/Users/t184h661/input_data.txt", read_data);
        // or provide the compelete path as below
        // $readmemb("D:/Testbences/input_output_files/input_data.txt", read_data);

        // total number of lines in input_data.txt = 6
        for (i=0; i<6; i=i+1)
        begin
            // 0_1_0_1 and 0101 are read in the same way, i.e.
            //a=0, b=1, sum_expected=0, carry_expected=0 for above line;
            // but use of underscore makes the values more readable.
            {G0,G1,G2,G3} = read_data[i]; // use this or below
            // {a, b, sum_carry_expected[0], sum_carry_expected[1]} = read_data[i];
            #20;  // wait for 20 clock cycle
        end
    end
endmodule

 

  
