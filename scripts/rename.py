import math

"""
Routines to rename atoms and residues from a 'labeled' step2_out.pdb file  ("0","+", or "-" tacked on the end) 

REVISION LOG
- 8-21-2007: VAV; spun these functions into their own python file 
- 10-10-2007: DLM: re-incorporating the proper handling of cysteine residues renamed CYD by MCCE which need to be renamed CYS2.
- 6-30-2009: DLM, additional bugfix relating to naming of CYS2, in this case it was messing up pdb formatting.
- 6-30-2009: DLM, additional bugfix relating to hydrogen and CD naming for NILE/CILE
- 7-1-2009: DLM, bugfix relating to handling of insertion ids; in cases where two consecutive residues (one of which had an insertion code but the same residue number) were the same amino acid, one residue would be omitted from the output, resulting in a consecutive sequence but a missing residue in the structure. Also fixed problem with naming of a hydrogen on GLH. 
- 8-19-2009: DLM, fixed a bug introduced at the last revision, wherein some N-terminal residues, when capped, would be split in two due to having two atoms with the same name. This had been introduced when fixing the insertion code bug.
- 8/25-2009: DLM, fixed hydrogen naming problem for ASH, wherein hydrogen needed to be named HD2, not HD1.
- 6/15/2012: DLM, allowing optional naming to GROMACS AMBER port format.

TO DO:
- See description of disulfide_search function -- need to fix naming for CYD residues that are not disulfide bonded.
"""


def rename_residues(pdbarr, renameTermini=True, terminology = 'AMBER'):
    """Convert residue names (and some heavy atom and hydrogen names) to AMBER (ffamber) format. This AMBER format is the one used by AMBER itself and by the GROMACS ffamber ports from the Sorin lab. New (gromacs 4.6) built-in AMBER ports have some slightly different naming (specify optional 'terminology' argument to get this) as discussed below.
    
    ARGUMENTS
        pdbarr - array of PDB atoms

    OPTIONAL ARGUMENTS
        terminology       default 'AMBER', which protonates residues using naming recognized by AMBER and the ffamber ports for GROMACS from the Sorin lab. 
                          Optionally, specify 'gAMBER' for the GROMACS AMBER format, which has some slightly different residue naming conventions 
                          (for example, LYP -> LYS, LYS -> LYN, and CYN -> CYS, CYS2 -> CYM )
        
    RETURNS
        pdbarr - updated array of PDB atoms with AMBER appropriate residue names
    """

    
    # DEBUG check.
    print("At start of renaming, pdbarr has", len(pdbarr), "items")
     
    # Transform the PDB file into a nested format that is easier to manipulate.
    npdb = nest_pdb(pdbarr)
    
    # DEBUG check.
    print("Nest/unnest leads to", len(unnest_pdb(npdb)), "items")

    # Convert residue and atom names to be appropriate for AMBER.
    npdb = rename_charged(npdb, terminology= terminology)
    npdb = histidine_search(npdb)
    npdb = disulfide_search(npdb, terminology = terminology)
    
    print('### renameTermini =', renameTermini)
    if (renameTermini):
        npdb = rename_termini(npdb)

    # Un-nest PDB
    pdbarr = unnest_pdb(npdb)
    
    # DEBUG check.
    #print "At end of renaming, pdbarr has ", len(pdbarr), "items"

    # Return the PDB file.
    return pdbarr

    


def rename_charged(npdb, terminology = 'AMBER'):
    """Generate AMBER-specific residue names for charged residues from MCCE residue names. Also fix some problems with atom naming (specifically hydrogens) for charged residues.
        
    ARGUMENTS
        npdb - "nested" PDB data structure generated by nest_pdb. Modified to reflect AMBER names.

    OPTIONAL ARGUMENTS
        terminology       default 'AMBER', which protonates residues using naming recognized by AMBER and the ffamber ports for GROMACS from the Sorin lab. 
                          Optionally, specify 'gAMBER' for the GROMACS AMBER format, which has some slightly different residue naming conventions 
                          (for example, LYP -> LYS, LYS -> LYN, and CYN -> CYS, CYS2 -> CYM )

    CHANGE LOG:
    - DLM 7-1-2009: Modified to fix naming of HE1 in GLH to HE2 to conform to ffamber rtp.
    """
        
    resname_and_state = list(map(lambda x:x[-1][17:20]+x[-1][-1],npdb))
    #print resname_and_state
    for i in range(len(npdb)):
        if (resname_and_state[i]=='HIS+'):
            npdb[i] = list(map(lambda x:x.replace('HIS','HIP'),npdb[i]))
        elif (resname_and_state[i]=='LYS0'):
            if terminology == 'AMBER':
                npdb[i] = list(map(lambda x:x.replace('LYS','LYN'),npdb[i]))
            elif terminology == 'gAMBER':
                npdb[i] = list(map(lambda x:x.replace('LYS','LYN'),npdb[i]))
        elif (resname_and_state[i]=='LYS+'):
            if terminology =='AMBER':
                npdb[i] = list(map(lambda x:x.replace('LYS','LYP'),npdb[i]))
            if terminology =='gAMBER':
                npdb[i] = list(map(lambda x:x.replace('LYS','LYS'),npdb[i]))
        elif (resname_and_state[i]=='CYS0'):
            if terminology =='AMBER':
                npdb[i] = list(map(lambda x:x.replace('CYS','CYN'),npdb[i]))
            elif terminology =='gAMBER':
                npdb[i] = list(map(lambda x:x.replace('CYS','CYS'),npdb[i]))
        elif (resname_and_state[i]=='CYS-'):
            npdb[i] = list(map(lambda x:x.replace('CYS','CYM'),npdb[i]))
        elif (resname_and_state[i]=='ASP0'):
            npdb[i] = list(map(lambda x:x.replace('ASP','ASH'),npdb[i]))
            #DLM 8/25/2009: ASH needs to have HD2, not HD1, for some reason
            npdb[i] = list(map(lambda x:x.replace('HD1 ASH','HD2 ASH'),npdb[i]))
        #Aspartate requires no sub
        elif (resname_and_state[i]=='GLU0'):
            npdb[i] = list(map(lambda x:x.replace('GLU','GLH'),npdb[i]))
            #DLM 7-1-2009: Fix GLY HE1 to HE2
            npdb[i] = list(map(lambda x:x.replace('HE1 GLH','HE2 GLH'),npdb[i]))
        # Glutamate requires no sub
        
        # Also, charge states for TYR are ignored....


    return npdb


def labeledPDB_to_AmberPDB(labeledPDBfile, outPDBfile, renameResidues=True):
    """Reads a 'labeled' PDB file written by MCCE (with "0","+", or "-" indicating the protonation state - see mcce.py)
    Example:
    ATOM      1  CA  LEU _0001_000  -8.847   7.195  16.727   1.700       0.000      BK____M000
    0
    ATOM      2  C   LEU _0001_000  -9.019   7.821  15.386   1.700       0.000      BK____M000
    0
    ....

    Writes an AMBER-residue-formatted PDB file, outPDBfile.
    """

    # Read in the pdb lines
    fin = open(labeledPDBfile,'r')
    lines = fin.readlines()
    fin.close()
    # Format so the even-numbered lines, "0", "+", "-", etc are supposed to be tacked onto the ends of each atom's line
    pdbarr = []
    while len(lines) > 0:
        pdbline = lines.pop(0)
        label = lines.pop(0)
        pdbarr.append( pdbline + label )
 
    if renameResidues:
        pdbarr=rename_residues(pdbarr)
    pdbarr=pdb_cleanup(pdbarr)
    
    # write AmberPDB to file
    fout = open(outPDBfile,'w')
    for line in pdbarr:
        fout.write(line)
    fout.close()


def renumber_atoms(pdbarr):
    """Renumbers atom entries (list items) of a PDB file so they are in sequence starting from 1.
    
    ARGUMENTS
        pdbarr - list of PDB atoms to be renumbered; mutated by call
    """
    
    # Renumber the atom entries in place.
    for i in range(len(pdbarr)):
        pdbarr[i]=pdbarr[i][0:6]+str(i+1).rjust(5)+pdbarr[i][11:]        

def rename_termini(npdb):
    """Renames the 'NTR' and 'CTR' residues generated by MCCE.
    Renames the O and OXT atoms at the C-terminus to OC1 and OC2 for AMBER.
    
    ARGUMENTS
        npdb - 

    """

    # Modified by Vincent Voelz August 1, 2008 to rename the termini for multiple chains

    # NOTES
    # Find all instances of 'NTR' and 'CTR'.  These names appear as different residues, even though they
    # demarcate the N- and C- terminal parts of the terminal residues

    # First find *all* instances of termini
    NTerminiRes = []
    CTerminiRes = []
    for i in range(0,len(npdb)):
        if (npdb[i][0][17:20] == 'NTR') | (npdb[i][0][17:20] == 'NTG'):
            NTerminiRes.append(i)
        if npdb[i][0][17:20] == 'CTR':
            CTerminiRes.append(i)
            
    print('### NTerminiRes:', NTerminiRes)
    print('### CTerminiRes:', CTerminiRes)
            
    # check to see if there are equal numbers of termini residues found
    if len(NTerminiRes) != len(CTerminiRes):
        raise "len(NTerminiRes) != len(CTerminiRes)"

    # Do renamimng for all pairs of termini found
    for k in range(0,len(CTerminiRes)):
        
        NResIndex = NTerminiRes[k]
        CResIndex = CTerminiRes[k]
        
        
        # Get three-letter residue names of N- and C-termini.
        ntrname = npdb[NResIndex+1][0][17:20]
        ctrname = npdb[CResIndex-1][0][17:20]
        
        print('### renaming NTR to', 'N'+ntrname)
        print('### renaming CTR to', 'C'+ctrname)
    
        # Rename N-terminal residue 'XXX' to 'NXXX'.
        for j in [NResIndex,NResIndex+1]:
            if ntrname=='LYS':
              for i in range(len(npdb[j])):
                npdb[j][i] = npdb[j][i][0:17]+'NLYP'+npdb[j][i][21:]
            else:
              for i in range(len(npdb[j])):
                npdb[j][i] = npdb[j][i][0:17]+'N'+ntrname+npdb[j][i][21:]
                #DLM 6/30/2009: As for VAV edit below in CILE case: use correct naming for CD (not CD1) for ILE/NILE:
                if ntrname=='ILE':
                    if npdb[j][i][13:16].split()[0]=='CD1':
                        npdb[j][i] = npdb[j][i][0:13]+'CD '+npdb[j][i][16:]
                    #DLM 6/30/2009: In NILE case, the hydrogen naming may also be incorrect
                    #in particular 1HD1 should be HD1, 2HD1 should be HD2, and 3HD1 should be HD3
                    if npdb[j][i][12:16].split()[0]=='1HD1':
                       npdb[j][i] = npdb[j][i][0:12]+' HD1'+npdb[j][i][16:]
                    elif npdb[j][i][12:16].split()[0]=='2HD1':
                       npdb[j][i] = npdb[j][i][0:12]+' HD2'+npdb[j][i][16:]
                    elif npdb[j][i][12:16].split()[0]=='3HD1':
                       npdb[j][i] = npdb[j][i][0:12]+' HD3'+npdb[j][i][16:]
                #End DLM 6/30/2009
                
        # Rename C-terminal residue from 'XXX' to 'CXXX', with some exceptions (noted below).
        # Also rename terminal oxygen atoms.
        for j in [CResIndex-1,CResIndex]:
            for i in range(len(npdb[j])):
                # VAV 5/14/2007: gmx ffamber does not have CLYN, only CLYP 
                if ctrname=='LYN':      
                    npdb[j][i] = npdb[j][i][0:17]+'CLYP'+npdb[j][i][21:]
                else:   
                    npdb[j][i] = npdb[j][i][0:17]+'C'+ctrname+npdb[j][i][21:]
                                
                # DLM 5/9/2007: Though this says that it changes the O and OXT names, it doesn't
                # Adding the below to do the renaming.
                if npdb[j][i][13:16].split()[0]=='O':
                    npdb[j][i] = npdb[j][i][0:13]+'OC1'+npdb[j][i][16:]
                elif npdb[j][i][13:16].split()[0]=='OXT':
                    npdb[j][i] = npdb[j][i][0:13]+'OC2'+npdb[j][i][16:]
                    
                #VAV 6/5/2007: gmx ffamber doesn't have "CD1" as an ILE/CILE atomname, only "CD"
                if ctrname=='ILE':
                    if npdb[j][i][13:16].split()[0]=='CD1':
                        npdb[j][i] = npdb[j][i][0:13]+'CD '+npdb[j][i][16:]
                    #DLM 6/30/2009: In NILE case, the hydrogen naming may also be incorrect
                    #in particular 1HD1 should be HD1, 2HD1 should be HD2, and 3HD1 should be HD3
                    if npdb[j][i][12:16].split()[0]=='1HD1':
                        npdb[j][i] = npdb[j][i][0:12]+' HD1'+npdb[j][i][16:]
                    elif npdb[j][i][12:16].split()[0]=='2HD1':
                        npdb[j][i] = npdb[j][i][0:12]+' HD2'+npdb[j][i][16:]
                    elif npdb[j][i][12:16].split()[0]=='3HD1':
                        npdb[j][i] = npdb[j][i][0:12]+' HD3'+npdb[j][i][16:]
                #End DLM 6/30/2009
    return npdb

def rename_MODELLER_termini(npdb):
    """Renames a nested pdb's N- and C- termini, including
    last residue's O and OXT (from MODELLER) to OC1 and OC2 (gromcs)."""

    # Find the N-terminal residue 
    NResIndex = 0
    while npdb[NResIndex][0].split()[0] != 'ATOM':
        NResIndex += 1

    # Find C-terminal residue
    CResIndex = -2 #  the last res should be an 'END' residue

    # Get three-letter residue names of N- and C-termini.
    ntrname = npdb[NResIndex][0][17:20]
    ctrname = npdb[CResIndex][0][17:20]

    if ntrname == 'LYS':
        ntrname = 'LYP'
    if ctrname == 'LYS':
        ctrname = 'LYP'

    print('### renaming NTR to', 'N'+ntrname)
    print('### renaming CTR to', 'C'+ctrname)

    # Rename N-terminal residue 'XXX' to 'NXXX'.
    for i in range(len(npdb[NResIndex])):
        npdb[NResIndex][i] = npdb[NResIndex][i][0:17]+'N'+ntrname+npdb[NResIndex][i][21:]

    # Rename C-terminal residue, including OXT
    for j in [CResIndex]:

            for i in range(len(npdb[j])):
                # VAV 5/14/2007: gmx ffamber does not have CLYN, only CLYP 
                if ctrname=='LYN':
                    npdb[j][i] = npdb[j][i][0:17]+'CLYP'+npdb[j][i][21:]
                else:
                    npdb[j][i] = npdb[j][i][0:17]+'C'+ctrname+npdb[j][i][21:]

                # DLM 5/9/2007: Though this says that it changes the O and OXT names, it doesn't
                # Adding the below to do the renaming.
                if npdb[j][i][13:16].split()[0]=='O':
                    npdb[j][i] = npdb[j][i][0:13]+'OC1'+npdb[j][i][16:]
                elif npdb[j][i][13:16].split()[0]=='OXT':
                    npdb[j][i] = npdb[j][i][0:13]+'OC2'+npdb[j][i][16:]
     
                #VAV 6/5/2007: gmx ffamber doesn't have "CD1" as an ILE/CILE atomname, only "CD"
                if ctrname=='ILE':  
                    if npdb[j][i][13:16].split()[0]=='CD1':
                        npdb[j][i] = npdb[j][i][0:13]+'CD '+npdb[j][i][16:]

    # Rename non-terminal lysines
    for j in range(len(npdb)):
      for i in range(len(npdb[j])):
          if npdb[j][i][17:20] == 'LYS':
              npdb[j][i] = npdb[j][i][0:17] + 'LYP' + npdb[j][i][20:]

    # Rename histidines
    for j in range(len(npdb)):
      for i in range(len(npdb[j])):
          if npdb[j][i][17:20] == 'HIS':
              npdb[j][i] = npdb[j][i][0:17] + 'HIP' + npdb[j][i][20:]

    return npdb
        
def nest_pdb(pdbarr):
    """Collect lines of the PDB file by residue.
    
    ARGUMENTS:
        pdbarr - list of lines from PDB file
        
    RETURNS
        nestedpdb - nested PDB file, such that nestedpdb[i][j] will be line j from residue i.
    """
    
    nestedpdb=[]
    residue=[]
    usedatoms = [] #DLM edit 7/1/2009
    for line in pdbarr:
        atom = line[12:17].strip() #DLM edit 7/1/2009
        if (len(residue) == 0):
            residue.append(line)
        else:
            #DLM 7/1/2009: The following should be OK even for residues with insertion codes (mcce removes the insertion code) EXCEPT if the two residues in sequence have the same residue name (in which case they will be packed into the same residue here). To fix this, store a list of atoms that are already found for the present residue and start a new residue anytime a second copy of an atom is found. See noted edits.
            #DLM 8/19/2009: This breaks cases of N-terminal residues, which may have two of the same atom names due to capping. Fix by only starting a new residue if the residue name is NOT NTR (which it will be if this is N-terminal) 
            if (line[17:27] == residue[-1][17:27]):
                #DLM 7/1/2009:
                if usedatoms.count(atom)==0:
                    usedatoms.append(atom)
                    residue.append(line) #Original line
                else: 
                    if not line[17:20]=='NTR' and not line[17]=='N':
                        #If we are finding a second copy of the atom it means we need to start a new residue EXCEPT if it is N-terminal
                        print("Starting new residue for:", line)
                        nestedpdb.append(residue)
                        residue=[line]
                        usedatoms=[atom]
                    else: #If it IS n-terminal, just save like before
                        residue.append(line)
                    
                #End DLM
            else:
                nestedpdb.append(residue)
                residue=[line]
                usedatoms=[atom]
    nestedpdb.append(residue)
    
    # Return the nexted PDB file.
    return nestedpdb

def unnest_pdb(npdb):
    """Expand the lines from the "nested" PDB file into a flat list of lines.
    
    ARGUMENTS
        npdb - "nested" PDB file; mutated in place
        
    RETURNS
        pdbarr - un-nested PDB file, such that pdbarr[i] will be line i from the PDB file
    """
    
    pdbarr=[]
    for res in npdb:
        for atm in res:
            pdbarr.append(atm)
    return pdbarr
    

def get_coords(atomname,residue):
    """Extract coordinates from given atom in list of PDB lines (such as all those lines for a residue in a nested PDB file).
    
    ARGUMENTS
        atomname - the name of the atom
        residue - list of lines from PDB file

    RETURNS
        (x,y,z) - tuple of atom coordinates, as floats
    
    """
    for n in range(len(residue)):
        if (residue[n][12:16].strip() == atomname.strip()):
            iX=float(residue[n][30:38])
            iY=float(residue[n][38:46])
            iZ=float(residue[n][46:54])
            return (iX,iY,iZ)

    raise "Atom not found!"        

def disulfide_search(npdb, min_dist = 1.8, max_dist = 2.2, terminology = 'AMBER'):
    """Rename CYS to CYX if it participates in a disulfide bond, as judged by distance range (inclusive). DLM modification: Also check for CYD, which is what MCCE names disulfides; we want to use the same checking criteria for those.
    
    ARGUMENTS
        npdb - nested PDB file
        
    OPTIONAL ARGUMENTS
        min_dist - minium distance cutoff for perceiving disulfide bond (default 1.8 A)
        max_dist - maximum distance cutoff for perceiving disulfide bond (default 2.2 A)
        terminology -- default AMBER, use gAMBER for GROMACS AMBER naming

    TO DO:
        Sometimes MCCE erroneously identifies a disulfide bond and renames the residues as CYD; these should be changed back in such cases.
    """
        
    residues_to_rename=set([])
    for i in range(len(npdb)):
        if (npdb[i][0][17:20] != 'CYS' and npdb[i][0][17:20] != 'CYD'):
            continue
        # Found a cysteine, now track down the sulfur
        iX,iY,iZ=get_coords('SG',npdb[i])
                
        for j in range(i+1,len(npdb)):
            if (npdb[j][0][17:20]!= 'CYS' and npdb[j][0][17:20] != 'CYD'):
                continue
            (jX,jY,jZ) = get_coords('SG',npdb[j])
                
            dX=iX-jX
            dY=iY-jY
            dZ=iZ-jZ

            distance = math.sqrt(dX*dX+dY*dY+dZ*dZ)
            if (distance >= min_dist and distance <= max_dist):
                residues_to_rename = residues_to_rename | set([i,j])
        
    # Rename the residues we selected
    for i in residues_to_rename:
        #DLM 6/30/2009: Additional bugfix -- replace 'CYS ' with 'CYS2', not 'CYS' with 'CYS2'
        if terminology=='AMBER':
            npdb[i] = list(map(lambda x:x.replace('CYS ','CYS2'),npdb[i]))
            npdb[i] = list(map(lambda x:x.replace('CYD ','CYS2'),npdb[i]))
        if terminology=='gAMBER':
            npdb[i] = list(map(lambda x:x.replace('CYS ','CYX'),npdb[i]))
            npdb[i] = list(map(lambda x:x.replace('CYD ','CYX'),npdb[i]))
        
    return npdb

def atom_is_present(pdblines, atomname):
    """Returns TRUE if the given atom is present in the given PDB atom lines.
    
    ARGUMENTS
        pdblines - list of PDB lines
        atomname - the name of the atom to check the existence of

    RETURNS
        is_present - True if the given atom name is present, False otherwise

    """

    is_present = False
    for pdbline in pdblines:
        if (pdbline[13:16] == atomname):
            is_present = True

    return is_present

def histidine_search(npdb):
    """Rename HIS residues to HID, HIE, or HIP by examining which protons are present.
    
    ARGUMENTS
        npdb - nested  PDB
    """
    
    for i in range(len(npdb)):
        resname = npdb[i][0][17:20]
        if (resname == 'HIS'):
            HE_present = atom_is_present(npdb[i], 'HE2') # bonded to NE2
            HD_present = atom_is_present(npdb[i], 'HD1') # bonded to ND1
            
            if (HD_present and HE_present):
                npdb[i] = list(map(lambda x:x.replace('HIS','HIP'),npdb[i]))
            elif (HE_present):
                npdb[i] = list(map(lambda x:x.replace('HIS','HIE'),npdb[i]))
            elif (HD_present):
                npdb[i] = list(map(lambda x:x.replace('HIS','HID'),npdb[i]))
            else:
                raise "No protons found for histidine."

    return npdb

def pdb_cleanup(pdbarr):
    """Remove extraneous entries from MCCE PDB files.
    
    ARGUMENTS
        pdbarr - list of PDB lines
        
    RETURNS
        updated_pdbarr - updated list of PDB lines
    """
    # Nuke everything after the coordinates
    # Use a default occupancy of 1 and a default B-factor of 0
    for i in range(len(pdbarr)):
        atom=pdbarr[i][0:54]
        # The atom symbol will be the first character after stripping
        # whitespace and numbers
        # NOTE: this will fail for atoms with more than one letter in their symbol
        #            eg, counterions
        atomsymbol = atom[12:16].strip(" 0123456789")[0]
        atom = atom + "1.00".rjust(6) + "0.00".rjust(6) + " "*10 + atomsymbol.rjust(2)+ " "*2
        pdbarr[i]=atom

    npdb=nest_pdb(pdbarr)

    for i in range(len(npdb)):
        # Set the residue index numbers
        # NOTE: We set chain identifier to blank, so this won't work for multi-chain PDBs
        for j in range(len(npdb[i])):
            atom = npdb[i][j]
            atom = atom[:21]+ " " + str(i+1).rjust(4)+ " "*4 + atom[30:]
            #print len(atom)
            npdb[i][j] = atom
            
    updated_pdbarr = unnest_pdb(npdb)
        
    return updated_pdbarr

            
