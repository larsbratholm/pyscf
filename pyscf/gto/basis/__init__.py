#!/usr/bin/env python
# -*- coding: utf-8
# Author: Qiming Sun <osirpt.sun@gmail.com>

import os
import sys
if sys.version_info < (2,7):
    import imp
else:
    import importlib
from pyscf.gto.basis import parse_nwchem

ALIAS = {
    'ano'        : 'ano.dat'        ,
    'anorcc'     : 'ano.dat'        ,
    'anoroosdz'  : 'roos-dz.dat'    ,
    'anoroostz'  : 'roos-tz.dat'    ,
    'roosdz'     : 'roos-dz.dat'    ,
    'roostz'     : 'roos-tz.dat'    ,
    'ccpvdz'     : 'cc-pvdz.dat'    ,
    'ccpvtz'     : 'cc-pvtz.dat'    ,
    'ccpvqz'     : 'cc-pvqz.dat'    ,
    'ccpv5z'     : 'cc-pv5z.dat'    ,
    'augccpvdz'  : 'aug-cc-pvdz.dat',
    'augccpvtz'  : 'aug-cc-pvtz.dat',
    'augccpvqz'  : 'aug-cc-pvqz.dat',
    'augccpv5z'  : 'aug-cc-pv5z.dat',
    'ccpvdzdk'   : 'cc-pvdz-dk.dat' ,
    'ccpvtzdk'   : 'cc-pvtz-dk.dat' ,
    'ccpvqzdk'   : 'cc-pvqz-dk.dat' ,
    'ccpv5zdk'   : 'cc-pv5z-dk.dat' ,
    'ccpvdzdkh'  : 'cc-pvdz-dk.dat' ,
    'ccpvtzdkh'  : 'cc-pvtz-dk.dat' ,
    'ccpvqzdkh'  : 'cc-pvqz-dk.dat' ,
    'ccpv5zdkh'  : 'cc-pv5z-dk.dat' ,
    'augccpvdzdk' : 'aug-cc-pvdz-dk.dat',
    'augccpvtzdk' : 'aug-cc-pvtz-dk.dat',
    'augccpvqzdk' : 'aug-cc-pvqz-dk.dat',
    'augccpv5zdk' : 'aug-cc-pv5z-dk.dat',
    'augccpvdzdkh': 'aug-cc-pvdz-dk.dat',
    'augccpvtzdkh': 'aug-cc-pvtz-dk.dat',
    'augccpvqzdkh': 'aug-cc-pvqz-dk.dat',
    'augccpv5zdkh': 'aug-cc-pv5z-dk.dat',
    'ccpvdzjkfit' : 'cc-pvdz-jkfit.dat' ,
    'ccpvtzjkfit' : 'cc-pvtz-jkfit.dat' ,
    'ccpvqzjkfit' : 'cc-pvqz-jkfit.dat' ,
    'ccpv5zjkfit' : 'cc-pv5z-jkfit.dat' ,
    'ccpvdzri'    : 'cc-pvdz-ri.dat'    ,
    'ccpvtzri'    : 'cc-pvtz-ri.dat'    ,
    'ccpvqzri'    : 'cc-pvqz-ri.dat'    ,
    'ccpv5zri'    : 'cc-pv5z-ri.dat'    ,
    'augccpvdzjkfit' : 'aug-cc-pvdz-jkfit.dat' ,
    'augccpvdzpjkfit': 'aug-cc-pvdzp-jkfit.dat',
    'augccpvtzjkfit' : 'aug-cc-pvtz-jkfit.dat' ,
    'augccpvqzjkfit' : 'aug-cc-pvqz-jkfit.dat' ,
    'augccpv5zjkfit' : 'aug-cc-pv5z-jkfit.dat' ,
    'heavyaugccpvdzjkfit' : 'heavy-aug-cc-pvdz-jkfit.dat',
    'heavyaugccpvtzjkfit' : 'heavy-aug-cc-pvtz-jkfit.dat',
    'augccpvdzri'    : 'aug-cc-pvdz-ri.dat'    ,
    'augccpvdzpri'   : 'aug-cc-pvdzp-ri.dat'   ,
    'augccpvqzri'    : 'aug-cc-pvqz-ri.dat'    ,
    'augccpvtzri'    : 'aug-cc-pvtz-ri.dat'    ,
    'ccpvtzdk3'   : 'cc-pVTZ-DK3.dat'   ,
    'ccpvqzdk3'   : 'cc-pVQZ-DK3.dat'   ,
    'augccpvtzdk3': 'aug-cc-pVTZ-DK3.dat',
    'augccpvqzdk3': 'aug-cc-pVQZ-DK3.dat',
    'dyalldz'    : 'dyall_dz'       ,
    'dyallqz'    : 'dyall_qz'       ,
    'dyalltz'    : 'dyall_tz'       ,
    'faegredz'   : 'faegre_dz'      ,
    'iglo'       : 'iglo3'          ,
    'iglo3'      : 'iglo3'          ,
    '321++g'     : os.path.join('pople-basis', '3-21++G.dat'   ),
    '321++g*'    : os.path.join('pople-basis', '3-21++Gs.dat'  ),
    '321++gs'    : os.path.join('pople-basis', '3-21++Gs.dat'  ),
    '321g'       : os.path.join('pople-basis', '3-21G.dat'     ),
    '321g*'      : os.path.join('pople-basis', '3-21Gs.dat'    ),
    '321gs'      : os.path.join('pople-basis', '3-21Gs.dat'    ),
    '431g'       : os.path.join('pople-basis', '4-31G.dat'     ),
    '631++g'     : os.path.join('pople-basis', '6-31++G.dat'   ),
    '631++g*'    : os.path.join('pople-basis', '6-31++Gs.dat'  ),
    '631++gs'    : os.path.join('pople-basis', '6-31++Gs.dat'  ),
    '631++g**'   : os.path.join('pople-basis', '6-31++Gss.dat' ),
    '631++gss'   : os.path.join('pople-basis', '6-31++Gss.dat' ),
    '631+g'      : os.path.join('pople-basis', '6-31+G.dat'    ),
    '631+g*'     : os.path.join('pople-basis', '6-31+Gs.dat'   ),
    '631+gs'     : os.path.join('pople-basis', '6-31+Gs.dat'   ),
    '631+g**'    : os.path.join('pople-basis', '6-31+Gss.dat'  ),
    '631+gss'    : os.path.join('pople-basis', '6-31+Gss.dat'  ),
    '6311++g'    : os.path.join('pople-basis', '6-311++G.dat'  ),
    '6311++g*'   : os.path.join('pople-basis', '6-311++Gs.dat' ),
    '6311++gs'   : os.path.join('pople-basis', '6-311++Gs.dat' ),
    '6311++g**'  : os.path.join('pople-basis', '6-311++Gss.dat'),
    '6311++gss'  : os.path.join('pople-basis', '6-311++Gss.dat'),
    '6311+g'     : os.path.join('pople-basis', '6-311+G.dat'   ),
    '6311+g*'    : os.path.join('pople-basis', '6-311+Gs.dat'  ),
    '6311+gs'    : os.path.join('pople-basis', '6-311+Gs.dat'  ),
    '6311+g**'   : os.path.join('pople-basis', '6-311+Gss.dat' ),
    '6311+gss'   : os.path.join('pople-basis', '6-311+Gss.dat' ),
    '6311g'      : os.path.join('pople-basis', '6-311G.dat'    ),
    '6311g*'     : os.path.join('pople-basis', '6-311Gs.dat'   ),
    '6311gs'     : os.path.join('pople-basis', '6-311Gs.dat'   ),
    '6311g**'    : os.path.join('pople-basis', '6-311Gss.dat'  ),
    '6311gss'    : os.path.join('pople-basis', '6-311Gss.dat'  ),
    '631g'       : os.path.join('pople-basis', '6-31G.dat'     ),
    '631g*'      : os.path.join('pople-basis', '6-31Gs.dat'    ),
    '631gs'      : os.path.join('pople-basis', '6-31Gs.dat'    ),
    '631g**'     : os.path.join('pople-basis', '6-31Gss.dat'   ),
    '631gss'     : os.path.join('pople-basis', '6-31Gss.dat'   ),
    'sto3g'      : 'sto-3g.dat'     ,
    'sto6g'      : 'sto-6g.dat'     ,
    'minao'      : 'minao'          ,
    'dz'         : 'dz.dat'         ,
    'dzpdunning' : 'dzp_dunning'    ,
    'dzvp'       : 'dzvp.dat'       ,
    'dzvp2'      : 'dzvp2.dat'      ,
    'dzp'        : 'dzp.dat'        ,
    'tzp'        : 'tzp.dat'        ,
    'qzp'        : 'qzp.dat'        ,
    'adzp'       : 'adzp.dat'       ,
    'atzp'       : 'atzp.dat'       ,
    'aqzp'       : 'aqzp.dat'       ,
    'dzpdk'      : 'dzp-dkh.dat'    ,
    'tzpdk'      : 'tzp-dkh.dat'    ,
    'qzpdk'      : 'qzp-dkh.dat'    ,
    'dzpdkh'     : 'dzp-dkh.dat'    ,
    'tzpdkh'     : 'tzp-dkh.dat'    ,
    'qzpdkh'     : 'qzp-dkh.dat'    ,
    'def2svp'    : 'def2-svp.dat'   ,
    'def2svpd'   : 'def2-svpd.dat'  ,
    'def2tzvpd'  : 'def2-tzvpd.dat' ,
    'def2tzvppd' : 'def2-tzvppd.dat',
    'def2tzvpp'  : 'def2-tzvpp.dat' ,
    'def2tzvp'   : 'def2-tzvp.dat'  ,
    'def2qzvpd'  : 'def2-qzvpd.dat' ,
    'def2qzvppd' : 'def2-qzvppd.dat',
    'def2qzvpp'  : 'def2-qzvpp.dat' ,
    'def2qzvp'   : 'def2-qzvp.dat'  ,
    'def2svpjfit'    : 'def2-svp-jfit.dat'   ,
    'def2svpjkfit'   : 'def2-svp-jkfit.dat'  ,
    'def2tzvpjfit'   : 'def2-tzvp-jfit.dat'  ,
    'def2tzvpjkfit'  : 'def2-tzvp-jkfit.dat' ,
    'def2tzvppjfit'  : 'def2-tzvpp-jfit.dat' ,
    'def2tzvppjkfit' : 'def2-tzvpp-jkfit.dat',
    'def2qzvpjfit'   : 'def2-qzvp-jfit.dat'  ,
    'def2qzvpjkfit'  : 'def2-qzvp-jkfit.dat' ,
    'def2qzvppjfit'  : 'def2-qzvpp-jfit.dat' ,
    'def2qzvppjkfit' : 'def2-qzvpp-jkfit.dat',
    'def2svpri'      : 'def2-svp-ri.dat'     ,
    'def2svpdri'     : 'def2-svpd-ri.dat'    ,
    'def2tzvpri'     : 'def2-tzvp-ri.dat'    ,
    'def2tzvpdri'    : 'def2-tzvpd-ri.dat'   ,
    'def2tzvppri'    : 'def2-tzvpp-ri.dat'   ,
    'def2tzvppdri'   : 'def2-tzvppd-ri.dat'  ,
    'def2qzvpri'     : 'def2-qzvp-ri.dat'    ,
    'def2qzvppri'    : 'def2-qzvpp-ri.dat'   ,
    'def2qzvppdri'   : 'def2-qzvppd-ri.dat'  ,
    'tzv'        : 'tzv.dat'        ,
    'weigend'    : 'weigend_cfit.dat',
    'weigend+etb': 'weigend_cfit.dat',
    'demon'      : 'demon_cfit.dat' ,
    'ahlrichs'   : 'ahlrichs_cfit.dat',
    'ccpvtzfit'  : 'cc-pvtz_fit.dat',
    'ccpvdzfit'  : 'cc-pvdz_fit.dat',
    'ccpwcvtzmp2fit': 'cc-pwCVTZ_MP2FIT.dat',
    'ccpvqzmp2fit': 'cc-pVQZ_MP2FIT.dat',
    'ccpv5zmp2fit': 'cc-pV5Z_MP2FIT.dat',
    'augccpwcvtzmp2fit': 'aug-cc-pwCVTZ_MP2FIT.dat',
    'augccpvqzmp2fit': 'aug-cc-pVQZ_MP2FIT.dat',
    'augccpv5zmp2fit': 'aug-cc-pV5Z_MP2FIT.dat',
    'ccpcvdz'    : ('cc-pvdz.dat', 'cc-pCVDZ.dat'),
    'ccpcvtz'    : ('cc-pvtz.dat', 'cc-pCVTZ.dat'),
    'ccpcvqz'    : ('cc-pvqz.dat', 'cc-pCVQZ.dat'),
    #'ccpcv5z'    : 'cc-pCV5Z.dat',
    'ccpcv6z'    : 'cc-pCV6Z.dat',
    'ccpwcvdz'   : ('cc-pvdz.dat', 'cc-pwCVDZ.dat'),
    'ccpwcvtz'   : 'cc-pwCVTZ.dat',
    'ccpwcvqz'   : 'cc-pwCVQZ.dat',
    'ccpwcv5z'   : 'cc-pwCV5Z.dat',
    'ccpwcvdzdk' : ('cc-pvdz.dat', 'cc-pwCVDZ-DK.dat'),
    'ccpwcvtzdk' : 'cc-pwCVTZ-DK.dat',
    'ccpwcvqzdk' : 'cc-pwCVQZ-DK.dat',
    'ccpwcvtzdk3': 'cc-pwCVTZ-DK3.dat',
    'ccpwcvqzdk3': 'cc-pwCVQZ-DK3.dat',
    'augccpwcvtzdk' : 'aug-cc-pwCVTZ-DK.dat',
    'augccpwcvqzdk' : 'aug-cc-pwCVQZ-DK.dat',
    'augccpwcvtzdk3': 'aug-cc-pwCVTZ-DK3.dat',
    'augccpwcvqzdk3': 'aug-cc-pwCVQZ-DK3.dat',
    'dgaussa1cfit': 'DgaussA1_dft_cfit.dat',
    'dgaussa1xfit': 'DgaussA1_dft_xfit.dat',
    'dgaussa2cfit': 'DgaussA2_dft_cfit.dat',
    'dgaussa2xfit': 'DgaussA2_dft_xfit.dat',
    'ccpvdzpp'   : 'cc-pvdz-pp.dat' ,
    'ccpvtzpp'   : 'cc-pvtz-pp.dat' ,
    'ccpvqzpp'   : 'cc-pvqz-pp.dat' ,
    'ccpv5zpp'   : 'cc-pv5z-pp.dat' ,
    'crenbl'     : 'crenbl.dat'     ,
    'crenbs'     : 'crenbs.dat'     ,
    'lanl2dz'    : 'lanl2dz.dat'    ,
    'lanl2tz'    : 'lanl2tz.dat'    ,
    'lanl08'     : 'lanl08.dat'     ,
    'sbkjc'      : 'sbkjc.dat'      ,
    'stuttgart'  : 'stuttgart_dz.dat',
    'stuttgartdz': 'stuttgart_dz.dat',
    'stuttgartrlc': 'stuttgart_dz.dat',
    'stuttgartrsc': 'stuttgart_rsc.dat',
    'ccpwcvdzpp' : 'cc-pwCVDZ-PP.dat',
    'ccpwcvtzpp' : 'cc-pwCVTZ-PP.dat',
    'ccpwcvqzpp' : 'cc-pwCVQZ-PP.dat',
    'ccpwcv5zpp' : 'cc-pwCV5Z-PP.dat',
    'ccpvdzppnr' : 'cc-pVDZ-PP-NR.dat',
    'ccpvtzppnr' : 'cc-pVTZ-PP-NR.dat',
    'augccpvdzpp': ('cc-pvdz-pp.dat', 'aug-cc-pVDZ-PP.dat'),
    'augccpvtzpp': ('cc-pvtz-pp.dat', 'aug-cc-pVTZ-PP.dat'),
    'augccpvqzpp': ('cc-pvqz-pp.dat', 'aug-cc-pVQZ-PP.dat'),
    'augccpv5zpp': ('cc-pv5z-pp.dat', 'aug-cc-pV5Z-PP.dat'),
    'pc0' : 'pc-0.dat',
    'pc1' : 'pc-1.dat',
    'pc2' : 'pc-2.dat',
    'pc3' : 'pc-3.dat',
    'pc4' : 'pc-4.dat',
    'augpc0' : 'aug-pc-0.dat',
    'augpc1' : 'aug-pc-1.dat',
    'augpc2' : 'aug-pc-2.dat',
    'augpc3' : 'aug-pc-3.dat',
    'augpc4' : 'aug-pc-4.dat',
    'pcseg0' : 'pcseg-0.dat',
    'pcseg1' : 'pcseg-1.dat',
    'pcseg2' : 'pcseg-2.dat',
    'pcseg3' : 'pcseg-3.dat',
    'pcseg4' : 'pcseg-4.dat',
    'augpcseg0' : 'aug-pcseg-0.dat',
    'augpcseg1' : 'aug-pcseg-1.dat',
    'augpcseg2' : 'aug-pcseg-2.dat',
    'augpcseg3' : 'aug-pcseg-3.dat',
    'augpcseg4' : 'aug-pcseg-4.dat',
# Burkatzki-Filippi-Dolg pseudo potential
    'bfdvdz'     : 'bfd_vdz.dat',
    'bfdvtz'     : 'bfd_vtz.dat',
    'bfdvqz'     : 'bfd_vqz.dat',
    'bfdv5z'     : 'bfd_v5z.dat',
    'bfd'        : 'bfd_pp.dat',
    'bfdpp'      : 'bfd_pp.dat',
#
    'ccpcvdzf12optri': os.path.join('f12-basis', 'cc-pCVDZ-F12-OptRI.dat'),
    'ccpcvtzf12optri': os.path.join('f12-basis', 'cc-pCVTZ-F12-OptRI.dat'),
    'ccpcvqzf12optri': os.path.join('f12-basis', 'cc-pCVQZ-F12-OptRI.dat'),
    'ccpvdzf12optri' : os.path.join('f12-basis', 'cc-pVDZ-F12-OptRI.dat' ),
    'ccpvtzf12optri' : os.path.join('f12-basis', 'cc-pVTZ-F12-OptRI.dat' ),
    'ccpvqzf12optri' : os.path.join('f12-basis', 'cc-pVQZ-F12-OptRI.dat' ),
    'ccpv5zf12'      : os.path.join('f12-basis', 'cc-pV5Z-F12.dat'       ),
    'ccpvdzf12rev2'  : os.path.join('f12-basis', 'cc-pVDZ-F12rev2.dat'   ),
    'ccpvtzf12rev2'  : os.path.join('f12-basis', 'cc-pVTZ-F12rev2.dat'   ),
    'ccpvqzf12rev2'  : os.path.join('f12-basis', 'cc-pVQZ-F12rev2.dat'   ),
    'ccpv5zf12rev2'  : os.path.join('f12-basis', 'cc-pV5Z-F12rev2.dat'   ),
    'ccpvdzf12nz'    : os.path.join('f12-basis', 'cc-pVDZ-F12-nZ.dat'    ),
    'ccpvtzf12nz'    : os.path.join('f12-basis', 'cc-pVTZ-F12-nZ.dat'    ),
    'ccpvqzf12nz'    : os.path.join('f12-basis', 'cc-pVQZ-F12-nZ.dat'    ),
    'augccpvdzoptri' : os.path.join('f12-basis', 'aug-cc-pVDZ-OptRI.dat' ),
    'augccpvtzoptri' : os.path.join('f12-basis', 'aug-cc-pVTZ-OptRI.dat' ),
    'augccpvqzoptri' : os.path.join('f12-basis', 'aug-cc-pVQZ-OptRI.dat' ),
    'augccpv5zoptri' : os.path.join('f12-basis', 'aug-cc-pV5Z-OptRI.dat' ),
}

def _is_pople_basis(basis):
    return (basis.startswith('631') or
            basis.startswith('321') or
            basis.startswith('431'))

_BASIS_DIR = os.path.dirname(__file__)

def _parse_pople_basis(basis, symb):
    if '(' in basis:
        mbas = basis[:basis.find('(')]
        extension = basis[basis.find('(')+1:basis.find(')')]
    else:
        mbas = basis
        extension = ''

    pathtmp = os.path.join('pople-basis',
                           mbas[0]+'-'+mbas[1:].upper() + '-polarization-%s.dat')
    def convert(s):
        if len(s) == 0:
            return []
        elif s[0].isalpha():
            return [pathtmp % s[0]] + convert(s[1:])
        else:
            return [pathtmp % s[:2]] + convert(s[2:])

    if symb in ('H', 'He'):
        if ',' in extension:
            return tuple([ALIAS[mbas]] + convert(extension.split(',')[1]))
        else:
            return ALIAS[mbas]
    else:
        return tuple([ALIAS[mbas]] + convert(extension.split(',')[0]))

def parse(string, symb=None):
    '''Parse the NWChem format basis or ECP text, return an internal basis (ECP)
    format which can be assigned to :attr:`Mole.basis` or :attr:`Mole.ecp`

    Args:
        string : Blank linke and the lines of "BASIS SET" and "END" will be ignored

    Examples:

    >>> mol = gto.Mole()
    >>> mol.basis = {'O': gto.basis.parse("""
    ... #BASIS SET: (6s,3p) -> [2s,1p]
    ... C    S
    ...      71.6168370              0.15432897
    ...      13.0450960              0.53532814
    ...       3.5305122              0.44463454
    ... C    SP
    ...       2.9412494             -0.09996723             0.15591627
    ...       0.6834831              0.39951283             0.60768372
    ...       0.2222899              0.70011547             0.39195739
    ... """)}
    '''
    if 'ECP' in string:
        return parse_nwchem.parse_ecp(string, symb)
    else:
        return parse_nwchem.parse(string, symb)

def parse_ecp(string, symb=None):
    return parse_nwchem.parse_ecp(string, symb)

def load(filename_or_basisname, symb):
    '''Convert the basis of the given symbol to internal format

    Args:
        filename_or_basisname : str
            Case insensitive basis set name. Special characters will be removed.
            or a string of "path/to/file" which stores the basis functions
        symb : str
            Atomic symbol, Special characters will be removed.

    Examples:
        Load STO 3G basis of carbon to oxygen atom

    >>> mol = gto.Mole()
    >>> mol.basis = {'O': load('sto-3g', 'C')}
    '''
    symb = ''.join([i for i in symb if i.isalpha()])
    if os.path.isfile(filename_or_basisname):
        # read basis from given file
        try:
            return parse_nwchem.load(filename_or_basisname, symb)
        except RuntimeError:
            with open(filename_or_basisname, 'r') as fin:
                return parse_nwchem.parse(fin.read(), symb)

    name = _format_basis_name(filename_or_basisname)
    if not (name in ALIAS or _is_pople_basis(name)):
        try:
            return parse_nwchem.parse(filename_or_basisname, symb)
        except KeyError:
            return parse_nwchem.parse(filename_or_basisname)
        except IndexError:
            raise RuntimeError('Basis %s not found' % filename_or_basisname)

    if name in ALIAS:
        basmod = ALIAS[name]
    elif _is_pople_basis(name):
        basmod = _parse_pople_basis(name, symb)
    else:
        raise RuntimeError('Basis %s not found' % filename_or_basisname)

    if 'dat' in basmod:
        b = parse_nwchem.load(os.path.join(_BASIS_DIR, basmod), symb)
    elif isinstance(basmod, (tuple, list)) and isinstance(basmod[0], str):
        b = []
        for f in basmod:
            b += parse_nwchem.load(os.path.join(_BASIS_DIR, f), symb)
    else:
        if sys.version_info < (2,7):
            fp, pathname, description = imp.find_module(basmod, __path__)
            mod = imp.load_module(name, fp, pathname, description)
            b = mod.__getattribute__(symb)
            fp.close()
        else:
            mod = importlib.import_module('.'+basmod, __package__)
            b = mod.__getattribute__(symb)
    return b

def load_ecp(filename_or_basisname, symb):
    '''Convert the basis of the given symbol to internal format
    '''
    symb = ''.join([i for i in symb if i.isalpha()])
    if os.path.isfile(filename_or_basisname):
        # read basis from given file
        try:
            return parse_nwchem.load_ecp(filename_or_basisname, symb)
        except RuntimeError:
            with open(filename_or_basisname, 'r') as fin:
                return parse_ecp(fin.read(), symb)

    name = _format_basis_name(filename_or_basisname)
    if name in ALIAS:
        basmod = ALIAS[name]
        return parse_nwchem.load_ecp(os.path.join(_BASIS_DIR, basmod), symb)
    else:
        return parse_ecp(filename_or_basisname, symb)

def _format_basis_name(basisname):
    return basisname.lower().replace('-', '').replace('_', '').replace(' ', '')
