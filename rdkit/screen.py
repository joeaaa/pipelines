import utils
import sys
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import MACCSkeys
from rdkit import DataStructs
from rdkit.Chem.Fingerprints import FingerprintMols
import gzip
import argparse

### start field name defintions #########################################

field_Similarity = "Similarity"

### start main execution #########################################

def main():

	descriptors = {
	    #'atompairs':   lambda m: Pairs.GetAtomPairFingerprint(m),
	    'maccs':       lambda m: MACCSkeys.GenMACCSKeys(m),
	    'morgan2':     lambda m: AllChem.GetMorganFingerprint(m,2),
	    'morgan3':     lambda m: AllChem.GetMorganFingerprint(m,3),
	    'rdkit':       lambda m: FingerprintMols.FingerprintMol(m),
	    #'topo':        lambda m: Torsions.GetTopologicalTorsionFingerprint(m)
	}

	metrics = {'asymmetric':DataStructs.AsymmetricSimilarity,
           'braunblanquet':DataStructs.BraunBlanquetSimilarity,
           'cosine':DataStructs.CosineSimilarity,
           'dice': DataStructs.DiceSimilarity,
           'kulczynski':DataStructs.KulczynskiSimilarity,
           'mcconnaughey':DataStructs.McConnaugheySimilarity,
           #'onbit':DataStructs.OnBitSimilarity,
           'rogotgoldberg':DataStructs.RogotGoldbergSimilarity,
           'russel':DataStructs.RusselSimilarity,
           'sokal':DataStructs.SokalSimilarity,
           'tanimoto': DataStructs.TanimotoSimilarity
           #'tversky': DataStructs.TverskySimilarity
           }
           
	### command line args defintions #########################################

	parser = argparse.ArgumentParser(description='RDKit screen')
	parser.add_argument('-smiles', help='query structure as smiles (incompatible with -molfile arg)')
	parser.add_argument('-molfile', help='query structure as filename in molfile format (incompatible with -smiles arg)')
	parser.add_argument('-simmin', type=float, default=0.7, help='similarity lower cutoff (1.0 means identical)')
	parser.add_argument('-simmax', type=float, default=999, help='similarity upper cutoff (1.0 means identical)')
	parser.add_argument('-d', '--descriptor', choices=['maccs','morgan2','morgan3','rdkit'], default='rdkit', help='descriptor or fingerprint type (default rdkit)')
	parser.add_argument('-m', '--metric',
                    choices=['asymmetric','braunblanquet','cosine','dice','kulczynski','mcconnaughey','rogotgoldberg','russel','sokal','tanimoto'],
                    default='tanimoto', help='similarity metric (default tanimoto)')
	parser.add_argument('-i', '--input', help="input SD file, if not defined the STDIN is used")
	parser.add_argument('-o', '--output', help="base name for output file (no extension). If not defined then SDTOUT is used for the structures and output is used as base name of the other files.")

	args = parser.parse_args()
	utils.log("Screen Args: ",args)

	descriptor = descriptors[args.descriptor]
	metric = metrics[args.metric.lower()]

	
	if args.smiles and args.molfile:
		raise ValueError('Cannot specify -smiles and -molfile arguments together')
	elif args.smiles:
		query_rdkitmol = Chem.MolFromSmiles(args.smiles)
	elif args.molfile:
		query_rdkitmol = Chem.MolFromMolFile(args.molfile)
	else:
		raise ValueError('No query structure specified')
	
	query_fp = descriptor(query_rdkitmol)

	input,output,suppl,writer,output_base = utils.defaultOpenInputOutput(args.input, args.output, 'screen')

	# OK, all looks good so we can hope that things will run OK.
	# But before we start lets write the metadata so that the results can be handled.
	t = open(output_base + '_types.txt', 'w')
	t.write(field_Similarity + '=integer\n')
	t.flush()
	t.close()

	i=0
	count = 0
	for mol in suppl:
	    i +=1
	    if mol is None: continue
	    target_fp = descriptor(mol)
	    sim = metric(query_fp, target_fp)
	
	    if sim > args.simmin and sim <= args.simmax:
	        count +=1
	        utils.log(i,sim)
	        for name in mol.GetPropNames():
	            mol.ClearProp(name)
	        mol.SetDoubleProp(field_Similarity, sim)
	        writer.write(mol)
        
	utils.log("Found",count,"similar molecules")

	writer.flush()
	writer.close()
	input.close()
	output.close()

	m = open(output_base  + '_metrics.txt', 'w')
	m.write('__InputCount__=' + str(i) + "\n")
	m.write('__OutputCount__=' + str(count) + "\n")
	m.write('RDKitScreen=' + str(i) + "\n")
	m.flush()
	m.close()


if __name__ == "__main__":
	main()

