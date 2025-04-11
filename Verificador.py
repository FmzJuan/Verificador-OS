import platform
import psutil
import socket
import os
import wmi
from datetime import datetime

def get_size(bytes, suffix="B"):
    """Escala bytes para formato legível"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor

def get_system_info():
    print("="*40, "INFORMAÇÕES DO SISTEMA", "="*40)
    uname = platform.uname()
    print(f"Nome do Sistema: {uname.system}")
    print(f"Nome do Computador: {uname.node}")
    print(f"Versão: {uname.version}")
    print(f"Release: {uname.release}")
    print(f"Arquitetura: {uname.machine}")
    print(f"Processador: {uname.processor}")
    print(f"Sistema operacional: {platform.system()} {platform.release()}")
    print(f"Versão do Windows: {platform.version()}")

def get_cpu_info():
    print("\n" + "="*40, "INFORMAÇÕES DA CPU", "="*40)
    print(f"Núcleos físicos: {psutil.cpu_count(logical=False)}")
    print(f"Núcleos lógicos: {psutil.cpu_count(logical=True)}")
    print(f"Frequência: {psutil.cpu_freq().current:.2f} MHz")
    print(f"Uso de CPU: {psutil.cpu_percent(interval=1)}%")

def get_memory_info():
    print("\n" + "="*40, "MEMÓRIA", "="*40)
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Disponível: {get_size(svmem.available)}")
    print(f"Usado: {get_size(svmem.used)}")
    print(f"Percentual: {svmem.percent}%")

def get_disk_info():
    print("\n" + "="*40, "DISCOS", "="*40)
    partitions = psutil.disk_partitions()
    c = wmi.WMI()
    drive_map = {disk.DeviceID: disk for disk in c.Win32_DiskDrive()}
    for partition in partitions:
        print(f"Disco: {partition.device}")
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"  Ponto de montagem: {partition.mountpoint}")
            print(f"  Sistema de arquivos: {partition.fstype}")
            print(f"  Total: {get_size(usage.total)}")
            print(f"  Usado: {get_size(usage.used)}")
            print(f"  Livre: {get_size(usage.free)}")
            print(f"  Percentual: {usage.percent}%")
        except PermissionError:
            continue

        # Verificar se é SSD
        drive_letter = partition.device.split(":")[0] + ":"
        for disk in drive_map.values():
            for partition_info in disk.Associators_("Win32_DiskDriveToDiskPartition"):
                for logical_disk in partition_info.Associators_("Win32_LogicalDiskToPartition"):

                    if logical_disk.DeviceID == drive_letter:
                        media_type = disk.MediaType or ""
                        is_ssd = "SSD" in (disk.Model or "") or "Solid State" in media_type
                        tipo = "SSD" if is_ssd else "HDD"
                        print(f"  Tipo: {tipo}")

def get_network_info():
    print("\n" + "="*40, "REDE", "="*40)
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"Hostname: {hostname}")
    print(f"Endereço IP: {ip_address}")
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == psutil.AF_LINK:
                print(f"Interface: {interface} -> MAC: {snic.address}")

def get_battery_info():
    print("\n" + "="*40, "BATERIA", "="*40)
    battery = psutil.sensors_battery()
    if battery:
        print(f"Percentual: {battery.percent}%")
        print(f"Plugado na tomada: {'Sim' if battery.power_plugged else 'Não'}")
        if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
            mins, secs = divmod(battery.secsleft, 60)
            print(f"Tempo restante: {mins} min {secs} seg")
    else:
        print("Bateria não detectada.")

def main():
    get_system_info()
    get_cpu_info()
    get_memory_info()
    get_disk_info()
    get_network_info()
    get_battery_info()
    
    print("\n" + "="*40)
    input("Digite 'ok' e pressione Enter para encerrar...")

if __name__ == "__main__":
    main()
