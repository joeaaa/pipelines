import utils, conformers
from rdkit import Chem, RDConfig
from rdkit.Chem import AllChem, rdMolAlign
import gzip
import argparse
import sys



### start field name defintions #########################################

field_O3DAScore = "O3DAScore"

### start function defintions #########################################

def doO3Dalign(i, mol, qmol, threshold, perfect_score, writer, conformerProps=None, minEnergy=None):
	pyO3As = rdMolAlign.GetO3AForProbeConfs(mol, qmol)
	best_score = 0
	j = 0
	conf_id = -1
	for pyO3A in pyO3As:
		align = pyO3A.Align()
		score = pyO3A.Score()
		if score > best_score:
			best_score = score
			conf_id = j
		j +=1
		
	#utils.log("Best score = ",best_score)
	if not threshold or perfect_score - best_score < threshold:
		utils.log(i,align,score,Chem.MolToSmiles(mol,isomericSmiles=True))
		mol.SetDoubleProp(field_O3DAScore, score)
		if conformerProps and minEnergy:
			eAbs = conformerProps[conf_id][(conformers.field_EnergyAbs)]
			eDelta = eAbs -minEnergy 
			if eAbs:
				mol.SetDoubleProp(conformers.field_EnergyAbs, eAbs)
			if eDelta:
				mol.SetDoubleProp(conformers.field_EnergyDelta, eDelta)
		writer.write(mol, confId=conf_id)

### start main execution #########################################

def main():

	parser = argparse.ArgumentParser(description='Open3DAlign with RDKit')
	parser.add_argument('query', help='query molfile')
	parser.add_argument('-t', '--threshold', type=float, help='score cuttoff relative to alignment of query to itself')
	parser.add_argument('-n', '--num', default=0, type=int, help='number of conformers to generate, if None then input structures are assumed to already be 3D')
	parser.add_argument('-a', '--attempts', default=0, type=int, help='number of attempts to generate conformers')
	parser.add_argument('-r', '--rmsd', type=float, default=1.0, help='prune RMSD threshold for excluding conformers')
	parser.add_argument('-e', '--emin', type=int, default=0, help='energy minimisation iterations for generated confomers (default of 0 means none)')
	parser.add_argument('-i', '--input', help='input SD file, if not defined the STDIN is used')
	parser.add_argument('-o', '--output', help="base name for output file (no extension). If not defined then SDTOUT is used for the structures and 'o3dalign' is used as base name of the other files.")


	args = parser.parse_args()
	utils.log("o3dAlign Args: ",args)

	qmol = Chem.MolFromMolFile(args.query)
	qmol = Chem.RemoveHs(qmol)
	qmol2 = Chem.MolFromMolFile(args.query)
	qmol2 = Chem.RemoveHs(qmol2)

	input,output,suppl,writer,output_base = utils.defaultOpenInputOutput(args.input, args.output, 'o3dalign')

	pyO3A = rdMolAlign.GetO3A(qmol2, qmol)
	perfect_align = pyO3A.Align()
	perfect_score = pyO3A.Score()
	utils.log('Perfect score:',perfect_align,perfect_score,Chem.MolToSmiles(qmol,isomericSmiles=True), qmol.GetNumAtoms())

	i=0
	count = 0
	for mol in suppl:
		if mol is None: continue
		if args.num > 0:
			conformerProps, minEnergy = conformers.process_mol_conformers(mol, i, args.num, args.attempts, args.rmsd, None, None, 0)
			mol = Chem.RemoveHs(mol)
			doO3Dalign(i, mol, qmol, args.threshold, perfect_score, writer, conformerProps=conformerProps, minEnergy=minEnergy)
		else:
			mol = Chem.RemoveHs(mol)
			doO3Dalign(i, mol, qmol, args.threshold, perfect_score, writer)
		i +=1
	
	input.close()
	writer.flush()
	writer.close()
	output.close()

if __name__ == "__main__":
	main()

