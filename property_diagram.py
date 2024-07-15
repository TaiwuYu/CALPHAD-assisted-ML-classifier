import matplotlib.pyplot as plt
import numpy as np
from tc_python import *
import pandas as pd
import csv
import matplotlib
#from interruptingcow import timeout

matplotlib.use('Agg')

db = "TCHEA6"
dep_el = "Ru"

#data=pd.read_csv(r'D:\\OSU research\\postdoc\\TC file\\HEA project\\comps_for_Taiwu_without_Ta_sub27.csv')
#data=pd.read_csv(r'D:\\OSU research\\postdoc\\TC file\\HEA project\\data1_pick.csv')
data=pd.read_csv(r'https://raw.githubusercontent.com/TaiwuYu/CALPHAD-assisted-ML-classifier/main/data1_pick.csv')


comp_id = pd.DataFrame(data,columns=['Composition_ID'])
comp_id = comp_id.to_numpy()

mo_comp = pd.DataFrame(data,columns=['Mo_mp'])
mo_comp = mo_comp.to_numpy()
nb_comp = pd.DataFrame(data,columns=['Nb_mp'])
nb_comp = nb_comp.to_numpy()
ti_comp = pd.DataFrame(data,columns=['Ti_mp'])
ti_comp = ti_comp.to_numpy()
zr_comp = pd.DataFrame(data,columns=['Zr_mp'])
zr_comp = zr_comp.to_numpy()
#ta_comp = pd.DataFrame(data,columns=['Ta_mp'])
#ta_comp = ta_comp.to_numpy()

data_length = len(mo_comp)
print("number of alloys =",data_length)
comp_temp = []
els = ["Mo","Nb","Ti","Zr"]
abandon=[]
T_liquid_start=[]
T_liquid_finish=[]
list_id=[]

for i in range(data_length):
    ID = comp_id[i]
    print('Composition_id',ID)
    temperature_out = []
    groups_density = []

    with TCPython(logging_policy=LoggingPolicy.FILE, log_file="comps_for_TY_sub.log") as start:
        try:
           start.set_cache_folder(os.path.basename(__file__) + "_cache")
           start.set_ges_version(6)
           calculation = (
              start.select_database_and_elements(db, [dep_el] + list(els)).get_system().
               with_property_diagram_calculation().
               with_axis(CalculationAxis(ThermodynamicQuantity.temperature()).
                      set_min(800).
                      set_max(3800).
                      with_axis_type(Linear().set_min_nr_of_steps(50))).
              set_condition(ThermodynamicQuantity.temperature(), 1000)
              .set_condition("X(Mo)",mo_comp[i]*0.01)
              .set_condition("X(Nb)",nb_comp[i]*0.01)
              .set_condition("X(Ti)",ti_comp[i]*0.01)
              .set_condition("X(Zr)",zr_comp[i]*0.01)
              ##.set_condition("X(Ta)",ta_comp[i]*0.01)
           )

           property_diagram = calculation.calculate()
           property_diagram.set_phase_name_style(PhaseNameStyle.ALL)

           # Here we get the volume fraction as a function of the temperature
           groups = \
            property_diagram.get_values_grouped_by_quantity_of(ThermodynamicQuantity.temperature(),
                                                           ThermodynamicQuantity.volume_fraction_of_a_phase(ALL_PHASES))

           #Here we get the density of system as a function of the temperature
           #groups_density = \
           #    property_diagram.get_values_grouped_by_quantity_of(ThermodynamicQuantity.temperature(),
           #                                                AbstractQuantity.density_of_system())
           #temperature_out = property_diagram.get_values_of(ThermodynamicQuantity.temperature())
           #print("temperature=",temperature_out)

           #groups_density = property_diagram.get_values_of(AbstractQuantity.density_of_system())
           #print("density=", groups_density)

        except Exception as e:
           print(f"Error processing composition ID:",ID)

    j=0
    for group in groups.values():
        plt.plot(group.x, group.y, label=group.label)


        #Here I screen all the phases.
        # If there are other phases in the system besides BCC and liquid along the entire temperature range, this alloy composition will be abandoned

        if (group.label[:6]!='BCC_B2' and group.label[:7]!='BCC_B2#2' and group.label[:7]!='BCC_B2#3' and group.label[:7]!='BCC_B2#4' and group.label[:6]!='LIQUID'):
            print("Abnormal case detected, phase is",group.label)
            abandon.append(ID)
        #else:
        #    with open("D:\OSU research\postdoc\TC file\HEA project\TY result\mfraction_compID{}_phase{}.csv".format(ID,j), "w") as f:
        #        writer = csv.writer(f)
        #        writer.writerow(group.label)
        #        writer.writerow(group.x)
        #        writer.writerow(group.y)


        if(group.label[:6]=='LIQUID'):
            try:
               print("T_liquid_start = ",group.x[0])
               print("T_liquid_end = ",group.x[group.y.index(1)])
               list_id.append(ID)
               T_liquid_start.append(group.x[0])
               T_liquid_finish.append(group.x[group.y.index(1)])
            except Exception as e:
                print(f"Error output temperature ID:", ID)


        j = j + 1

    plt.xlabel("Temperature [K]")
    plt.ylabel("Volume fraction of phases [-]")
    plt.legend(loc="center right")
    plt.title("HEA property diagram composition ID{}".format(ID))
    plt.savefig('D:\OSU research\postdoc\TC file\HEA project\TY result\compID{}.png'.format(ID), bbox_inches='tight')
    plt.close()

    if(i%25==0):
        with open("D:\OSU research\postdoc\TC file\HEA project\TY result\eutectic_temp_new{}.csv".format(i), "w") as f:
            writer = csv.writer(f)
            writer.writerow(list_id)
            writer.writerow(T_liquid_start)
            writer.writerow(T_liquid_finish)





    #for group in groups_density.values():
    #plt.plot(temperature_out, groups_density)
    #plt.xlabel("Temperature [K]")
    #plt.ylabel("Density")
    #plt.title("HEA density composition ID{}".format(ID))
    #plt.savefig('D:\OSU research\postdoc\TC file\HEA project\TY result\density_compID{}.png'.format(ID), bbox_inches='tight')
    #plt.close()
with open("D:\OSU research\postdoc\TC file\HEA project\TY result\eutectic_temp.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(list_id)
    writer.writerow(T_liquid_start)
    writer.writerow(T_liquid_finish)

print("Abandoned ID:",abandon)
    #plt.show()
