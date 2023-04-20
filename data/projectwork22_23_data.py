# ==============================================================================
# description     :Data for the project work
# author          :Roberto Pinto
# date            :2022.04.21
# version         :1.0
# notes           :This software is meant for teaching purpose only and it is provided as-is under the GPL license.
# ==============================================================================

# Data
from data_structures import Warehouse, Customer, import_data

customers_as_is = [
            'Milan;45.4669;9.19;2300',
            'Turin;45.0667;7.7;1871',
            'Genoa;44.4072;8.934;1580',
            'Bologna;44.4939;11.3428;889',
            'Monza;45.5836;9.2736;124',
            'Bergamo;45.695;9.67;1521',
            'Novara;45.45;8.6167;704',
            'Piacenza;45.05;9.7;803',
            'Alessandria;44.9133;8.62;94',
            'Busto Arsizio;45.612;8.8518;83',
            'Como;45.8103;9.0861;283',
            'Sesto San Giovanni;45.5333;9.2333;182',
            'Varese;45.8167;8.8333;81',
            'Asti;44.9;8.2069;176',
            'Cinisello Balsamo;45.55;9.2167;176']

customers_after_merge = [
            'Milan;45.4669;9.19;2300',
            'Turin;45.0667;7.7;1871',
            'Genoa;44.4072;8.934;1580',
            'Bologna;44.4939;11.3428;889',
            'Monza;45.5836;9.2736;124',
            'Bergamo;45.695;9.67;1521',
            'Novara;45.45;8.6167;704',
            'Piacenza;45.05;9.7;803',
            'Alessandria;44.9133;8.62;94',
            'Busto Arsizio;45.612;8.8518;83',
            'Como;45.8103;9.0861;283',
            'Sesto San Giovanni;45.5333;9.2333;182',
            'Varese;45.8167;8.8333;81',
            'Asti;44.9;8.2069;176',
            'Cinisello Balsamo;45.55;9.2167;176',
            'Venice;45.4397;12.3319;261',
            'Verona;45.4386;10.9928;1257',
            'Padova;45.4064;11.8778;2210',
            'Trieste;45.6503;13.7703;204',
            'Brescia;45.5389;10.2203;2197',
            'Parma;44.8015;10.328;996',
            'Modena;44.6458;10.9257;385',
            'Reggio Emilia;44.7;10.6333;272',
            'Ravenna;44.4178;12.1994;159',
            'Ferrara;44.8353;11.6199;132',
            'Trento;46.0667;11.1167;918',
            'Vicenza;45.55;11.55;112',
            'Bolzano;46.5;11.35;707',
            'Udine;46.0667;13.2333;200',
            'Mestre;45.4906;12.2381;89',
            'Treviso;45.6722;12.2422;985']

warehouses_as_is = ['Bergamo;45.695;9.67;4800;100000',
                    'Genoa;44.4072;8.934;5300;123000',
                    'Piacenza;45.05;9.7;2800;60000']

warehouses_after_merge = [
                    'Bergamo;45.695;9.67;4800;100000',
                    'Genoa;44.4072;8.934;5300;123000',
                    'Piacenza;45.05;9.7;2800;60000',
                    'Padova;45.4064;11.8778;4700;100000',
                    'Novara;45.45;8.6167;2200;90000',
                    'Verona;45.4386;10.9928;4500;50000',
]

warehouses_after_merge_plus_alternatives = [
                    'Bergamo;45.695;9.67;4800;100000',
                    'Genoa;44.4072;8.934;5300;123000',
                    'Piacenza;45.05;9.7;2800;60000',
                    'Padova;45.4064;11.8778;4700;100000',
                    'Novara;45.45;8.6167;2200;90000',
                    'Verona;45.4386;10.9928;4500;50000',
                    'Milan;45.4669;9.19;8000;145000',
                    'Turin;45.0667;7.7;7000;120000',
                    'Bologna;44.4939;11.3428;7000;100000',
                    'Bolzano;46.5;11.35;4500;87000',
                    'Bergamo_extended;45.695;9.67;9000;190000',
                    'Verona_extended;45.4386;10.9928;6500;90000',
]

customers_as_is = import_data(customers_as_is, 'customer')
customers_after_merge = import_data(customers_after_merge, 'customer')

warehouses_as_is = import_data(warehouses_as_is, 'warehouse')
warehouses_after_merge = import_data(warehouses_after_merge, 'warehouse')
warehouses_after_merge_plus_alternatives = import_data(warehouses_after_merge_plus_alternatives, 'warehouse')
