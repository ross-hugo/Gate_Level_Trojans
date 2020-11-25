#!/usr/bin/env python
import sys
import os
from copy import deepcopy

graph_nodes = {}
graph_edges = {}

trojan_nodes = {}
trojan_edges = {}

trojan_edges_copy = {}

all_text = []
troj_text = []

global_output = ""

num_modules = 0
main_module = ""

assign_trojan = {}

def check_file():
    if len(sys.argv) != 4:
        raise ValueError("Provide 2 input files of the gate level description and the Trojan and a gate to confuse")

def check_module():
    global num_modules, main_module
    mod_names = []
    with open(str(sys.argv[1]), 'r') as f:
        for line in f:
            if "module" in line.lower() and not "endmodule" in line.lower():
                num_modules += 1
                t_line = line.strip()
                mod_list = t_line.split(" ", 1)[1]
                mod_name = mod_list.split("(", 1)[0].strip()
                mod_names.append(mod_name)
    with open(str(sys.argv[1]), 'r') as f:
        if num_modules > 1:
            final_names = []
            for name in mod_names:
                is_useable = True
                for line in f:
                    if name in line.lower():
                        is_useable = False
                if is_useable:
                    final_names.append(name)
            main_module = final_names[0]
            return final_names[0]

def parse_file_netlist():
    module_name = check_module()
    with open(str(sys.argv[1]), 'r') as f:
        start = False
        for line in f:
            all_text.append(line)
            if "module" in line and module_name in line:
            # if ("module" in line) and ("GND" in line):
                start = True
            elif "input" in line and start:
                t_line = line.strip()[6:-1]
                list_inputs = t_line.split(',')
                for inp in list_inputs:
                    inp = inp.strip()
                    if inp not in graph_nodes:
                        graph_nodes[inp] = {}
                    graph_nodes[inp]["is_input"] = True
                    graph_nodes[inp]["is_output"] = False
                    graph_nodes[inp]['control'] = [1,1]
            elif "output" in line and start:
                global_output = line.strip()[7:-1].strip()
                if global_output not in graph_nodes:
                    graph_nodes[global_output] = {}
                graph_nodes[global_output]["is_input"] = False
                graph_nodes[global_output]["is_output"] = True
                graph_nodes[global_output]["control"] = [1,1]
            elif "wire" in line and start:
                #just adding the gates to the graph_nodes
                t_line = line.strip()[5:]
                t_line = t_line.replace(";", "")
                all_names = t_line.split(',')
                for name in all_names:
                    node_name = name.strip()
                    if node_name not in graph_nodes:
                        graph_nodes[node_name] = {}
                        graph_nodes[node_name]["is_output"] = False
                        graph_nodes[node_name]["is_input"] = False
                        graph_nodes[node_name]['control'] = [1,1]
            elif "add" in line.lower() or "or" in line.lower() \
                    or "nor" in line.lower() or "dff" in line.lower() \
                    or "and" in line.lower() or "nand" in line.lower():
                #add specifications of nodes
                t_line = line.strip()
                t_line = t_line.replace(";", "")
                gate = t_line.split(' ', 1)[0].lower()
                gate_desc = t_line.split(' ', 1)[1]
                gate_inputs_output = gate_desc[gate_desc.find("(")+1:gate_desc.find(")")]
                gate_io_list = gate_inputs_output.split(",")
                output = gate_io_list[0].strip()
                input1 = gate_io_list[1].strip()
                input2 = gate_io_list[2].strip()
                name = gate_desc.split("(",1)[0].strip()
                if output in graph_nodes:
                    graph_nodes[output]["type"] = gate
                    graph_nodes[output]["is_output"] = True
                    graph_nodes[output]["inputs"] = [input1, input2]
                    graph_nodes[output]["name"] = name
                if input1 in graph_nodes:
                    graph_nodes[input1]["is_input"] = True
                if input2 in graph_nodes:
                    graph_nodes[input2]["is_input"] = True

                #also add the edges to create the graph
                if input1 not in graph_edges:
                    graph_edges[input1] = set()
                if input2 not in graph_edges:
                    graph_edges[input2] = set()
                graph_edges[input1].add(output)
                graph_edges[input2].add(output)
            elif "not" in line.lower():
                t_line = line.strip()
                t_line = t_line.replace(";", "")
                gate = t_line.split(' ', 1)[0].lower()
                gate_desc = t_line.split(' ', 1)[1]
                gate_inputs_output = gate_desc[gate_desc.find("(")+1:gate_desc.find(")")]
                gate_io_list = gate_inputs_output.split(",")
                output = gate_io_list[0].strip()
                input1 = gate_io_list[1].strip()
                if output not in graph_nodes:
                    graph_nodes[output] = {}
                graph_nodes[output]["type"] = gate
                graph_nodes[output]["is_output"] = True
                graph_nodes[output]["inputs"] = [input1, input1]
                if input1 not in graph_nodes:
                    graph_nodes[input1] = {}
                graph_nodes[input1]["is_input"] = True

                if input1 not in graph_edges:
                    graph_edges[input1] = set()
                graph_edges[input1].add(output)

def parse_file_trojan():
    with open(str(sys.argv[2]), 'r') as f:
        for line in f:
            troj_text.append(line)
            if "wire" in line:
                #just adding the gates to the trojan
                t_line = line.strip()[5:]
                all_names = t_line.split(',')
                for name in all_names:
                    node_name = name.strip()
                    if "victim" in node_name:
                        node_name = global_output + "_x"
                    trojan_nodes[node_name] = {}
                    trojan_nodes[node_name]["is_output"] = False
                    trojan_nodes[node_name]["is_input"] = False
            elif "nor" in line.lower() or "nand" in line.lower() \
                    or "or" in line.lower() or "and" in line.lower():
                t_line = line.strip()
                gate = t_line.split(' ', 1)[0]
                gate_desc = t_line.split(' ', 1)[1]
                gate_inputs_output = gate_desc[gate_desc.find("(")+1:gate_desc.find(")")]
                gate_io_list = gate_inputs_output.split(",")
                output = gate_io_list[0].strip()
                if "victim" in output:
                    output = global_output + "_x"
                input1 = gate_io_list[1].strip()
                input2 = gate_io_list[2].strip()
                if output in trojan_nodes:
                    trojan_nodes[output]["type"] = gate
                    trojan_nodes[output]["is_output"] = True

                if input1 in trojan_nodes:
                    trojan_nodes[input1]["is_input"] = True
                if input2 in trojan_nodes:
                    trojan_nodes[input2]["is_input"] = True
            
                #add node edges in trojan
                if input1 not in trojan_edges:
                    trojan_edges[input1] = set()
                if input2 not in trojan_edges:
                    trojan_edges[input2] = set()
                trojan_edges[input1].add(output)
                trojan_edges[input2].add(output)

def find_starting():
    return [x for x in graph_nodes if \
            not graph_nodes[x]["is_output"] and \
            graph_nodes[x]["is_input"]]

def calc_control(starting_nodes):
    #starting_nodes has to be a list of names of nodes
    queue = []
    for node in graph_nodes:
        if "inputs" in graph_nodes[node]:
            queue.append(node)

    while len(queue) != 0:
        node = queue.pop(0)
        inp1 = graph_nodes[node]["inputs"][0]
        inp2 = graph_nodes[node]["inputs"][1]

        if graph_nodes[node]["type"] == "nor":
            graph_nodes[node]["control"][0] = \
                min(graph_nodes[inp1]["control"][1],\
                    graph_nodes[inp2]['control'][1]) + 1
            graph_nodes[node]['control'][1] = \
                graph_nodes[inp1]['control'][0] + \
                graph_nodes[inp2]['control'][0] + 1

        elif graph_nodes[node]["type"] == "not":
            graph_nodes[node]['control'][0] = \
                graph_nodes[inp1]['control'][1] + 1
            graph_nodes[node]['control'][1] = \
                graph_nodes[inp1]['control'][0] + 1

        elif graph_nodes[node]["type"] == "xor":
            graph_nodes[node]['control'][0] = min(\
                graph_nodes[inp1]['control'][0] +\
                graph_nodes[inp2]['control'][0],\
                graph_nodes[inp1]['control'][1]+ \
                graph_nodes[inp2]['control'][1] ) + 1
            graph_nodes[node]['control'][1] = min(\
                graph_nodes[inp1]['control'][1] +\
                graph_nodes[inp2]['control'][0],\
                graph_nodes[inp2]['control'][1] +\
                graph_nodes[inp2]['control'][0]) + 1

        elif graph_nodes[node]["type"] == "and":
            graph_nodes[node]['control'][0] = min(\
                graph_nodes[inp1]['control'][0],\
                graph_nodes[inp2]['control'][0]) + 1
            graph_nodes[node]['control'][1] = \
                graph_nodes[inp1]['control'][1] +\
                graph_nodes[inp2]['control'][1] + 1

        elif graph_nodes[node]["type"] == "or":
            graph_nodes[node]['control'][0] = \
                graph_nodes[inp1]['control'][0] + \
                graph_nodes[inp2]['control'][0] + 1
            graph_nodes[node]['control'][1] = min(\
                graph_nodes[inp1]['control'][1],\
                graph_nodes[inp2]['control'][1]) + 1

        elif graph_nodes[node]["type"] == "nand":
            graph_nodes[node]['control'][0] = \
                graph_nodes[inp1]['control'][1] + \
                graph_nodes[inp2]['control'][1] + 1
            graph_nodes[node]['control'][1] = min(\
                graph_nodes[inp1]['control'][0],\
                graph_nodes[inp2]['control'][0]) + 1

        else:
            graph_nodes[node]["control"][0] = \
                min(graph_nodes[inp1]["control"][0], \
                graph_nodes[inp2]["control"][0]) + 1
            graph_nodes[node]["control"][1] = \
                min(graph_nodes[inp1]["control"][1], \
                graph_nodes[inp2]["control"][1]) + 1

def calculate_controlability():
    start_nodes = find_starting()
    #here should change something in the graph_nodes for control value
    calc_control(start_nodes)

def remove_unused_nodes():
    graph_keys = list(graph_nodes.keys())
    for node in graph_keys:
        if not graph_nodes[node]["is_output"] \
            and not graph_nodes[node]["is_input"]:
            del graph_nodes[node]

    trojan_keys = list(trojan_nodes.keys())
    for node in trojan_keys:
        if not trojan_nodes[node]["is_output"] \
            and not trojan_nodes[node]["is_input"]:
            del trojan_nodes[node]

def lowest_controllability():
    count = 0
    ret = []
    for n in trojan_edges:
        if n[0].lower() == "i":
            count += 1
    seen = set()
    used = 0
    while used < count:
        largest_node = ""
        max_c = 0
        for node in graph_nodes:
            if node not in seen and node != global_output:
                if max(graph_nodes[node]['control']) > max_c:
                    max_c = max(graph_nodes[node]['control'])
                    largest_node = node
                    seen.add(node)
        ret.append(largest_node)
        used += 1
    return ret

def insert_trojan():
    global trojan_edges_copy, assign_trojan
    #find the lowest controllability
    lowest_nodes = lowest_controllability()
    #insert the new one in graph
    count = 0
    troj_keys = list(trojan_edges.keys())
    trojan_edges_copy = deepcopy(trojan_edges)
    for n in troj_keys:
        if n.lower()[0] == "i" and n not in global_output:
            assign_trojan[n] = lowest_nodes[count]
            #trojan_edges[lowest_nodes[count]] = trojan_edges.pop(n)
            #troj_to_n[n] = lowest_nodes[count]

            count += 1
    #combine graphs
    new_troj_keys = list(trojan_edges.keys())
    for n in new_troj_keys:
        if n in graph_edges:
            graph_edges[n] = graph_edges[n] | trojan_edges[n]
        else:
            graph_edges[n] = set()
            graph_edges[n] = graph_edges[n] | trojan_edges[n]

    #trojan_edges

def write_trojan(name):
    with open(name, 'w') as f:
        f.write("-"*40 + "\n")
        f.write("Trojan Template\n")
        f.write("-"*40 + "\n\n")
    os.system("cat " + str(sys.argv[2]) + " >> " + str(name))

def write_design(name):
    with open(name, 'a') as f:
        f.write("-"*40 + "\n")
        f.write("Design Before Trojan Insertion\n")
        f.write("-"*40 + "\n\n")
    os.system("cat " + str(sys.argv[1]) + " >> " + str(name))
    with open(name, 'a') as f:
        f.write("\n" + "-"*40 + "\n")
        f.write("Nets " + ','.join([assign_trojan[x] for x in assign_trojan]) + \
        """ Activates the Trojan (i.e. trigger nets) \nand Net """ + global_output +\
        """ is impacted by the payload (victim)""")
        f.write("\n" + "-"*40 + "\n")

def has_gate(the_line_of_t):
    if "and " in the_line_of_t.lower() or \
        "nand " in the_line_of_t.lower() or \
        "or " in the_line_of_t.lower() or \
        "nand " in the_line_of_t.lower() or \
        "xor " in the_line_of_t.lower() or \
        "not " in the_line_of_t.lower():
            return True
    return False

def is_input(line):
    t_line = line.strip()
    t_line = t_line.replace(";", "")
    gate = t_line.split(' ', 1)[0].lower()
    gate_desc = t_line.split(' ', 1)[1]
    gate_inputs_output = gate_desc[gate_desc.find("(")+1:gate_desc.find(")")]
    gate_io_list = gate_inputs_output.split(",")
    input1 = gate_io_list[1].strip()
    input2 = ""
    if gate != "not":
        input2 = gate_io_list[2].strip()
    if global_output == input1 or global_output == input2:
        return True
    return False

def write_with_trojan(name):
    global trojan_edges_copy
    seen_module, seen_wire, start = False, False, True
    with open(name, 'a') as f:
        for past_text in all_text:
            if seen_module and seen_wire and start:
                wire_str = "\t\twire "
                for n in trojan_nodes:
                    if global_output not in n:
                        wire_str += str(n) + ", "
                # for n in trojan_edges_copy:
                #     wire_str += (str(trojan_edges_copy[n]) + ", ")
                for n in assign_trojan:
                    wire_str += str(n) + ", "
                wire_str += global_output + "_x;"
                # wire_str = wire_str[:-2] + ";"
                f.write(wire_str + "\n\n")
                start = False
            elif main_module in past_text:
                seen_module = True
                f.write(past_text + "\n")
            elif "wire" in past_text:
                seen_wire = True
                f.write(past_text + "\n")
            elif "endmodule" in past_text:
                continue
            else:
                if global_output in past_text:
                    # if has_gate(past_text):
                    #     if not is_input(past_text):
                    past_text = past_text.replace(global_output, global_output + "_x")
                f.write(past_text)
        
        for troj in assign_trojan:
            f.write("\tassign " + str(troj) + "= " + str(assign_trojan[troj]) + ";\n")
        f.write("\n")

        seen_wire = False
        for text in troj_text:
            if seen_wire:
                if "victim" not in text:
                    if text.isspace():
                        continue
                    f.write("\t\t" + text)
                else:
                    text = text.replace("victim_x", global_output)
                    text = text.replace("victim", global_output + "_x")
                    f.write("\t\t" + text)
            else:
                if "wire" in text:
                    seen_wire = True
        f.write("endmodule\n")
    

def display_results():
    filename = "netlist_w_trojan.v"
    write_trojan(filename)
    write_design(filename)
    write_with_trojan(filename)


def main():
    global global_output
    global_output = sys.argv[3]
    check_file()
    parse_file_netlist()
    parse_file_trojan()
    remove_unused_nodes()
    calculate_controlability()
    insert_trojan()
    display_results()

    print("done")

if __name__ == "__main__":
    main()
