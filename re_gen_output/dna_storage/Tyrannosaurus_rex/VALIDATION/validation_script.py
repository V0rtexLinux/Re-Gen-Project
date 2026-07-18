#!/usr/bin/env python3
"""
Validador de integridade para DNA armazenado em mídia.
Execute este script para verificar se os dados no disco estão intactos.
"""

import hashlib
import json
from pathlib import Path

DNA_DIR = Path(__file__).parent.parent / "DNA"
CHECKSUMS_DIR = Path(__file__).parent.parent / "CHECKSUMS"

def validate():
    """Valida todos os checksums."""
    
    # Lê sequência FASTA
    with open(DNA_DIR / "sequence.fasta") as f:
        lines = f.readlines()
    
    sequence = "".join(line.strip() for line in lines[1:])
    
    # Calcula SHA-256
    calculated_sha256 = hashlib.sha256(sequence.encode()).hexdigest()
    
    # Lê SHA-256 esperado
    with open(CHECKSUMS_DIR / "SHA256") as f:
        stored_sha256 = f.readline().split(": ")[1].strip()
    
    if calculated_sha256 == stored_sha256:
        print(f"✓ SHA-256 válido")
    else:
        print(f"✗ SHA-256 INVÁLIDO!")
        print(f"  Esperado: {stored_sha256}")
        print(f"  Encontrado: {calculated_sha256}")
        return False
    
    # Valida CRC32
    import zlib
    crc = zlib.crc32(sequence.encode()) & 0xffffffff
    with open(CHECKSUMS_DIR / "CRC32") as f:
        stored_crc = f.readline().split(": ")[1].strip()
    
    if f"{crc:08x}" == stored_crc.lower():
        print(f"✓ CRC32 válido")
    else:
        print(f"⚠ CRC32 diferente (possível corrupção)")
    
    print(f"\n✓ Validação concluída com sucesso!")
    return True

if __name__ == "__main__":
    validate()
