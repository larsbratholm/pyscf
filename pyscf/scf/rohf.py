#!/usr/bin/env python
#
# Author: Qiming Sun <osirpt.sun@gmail.com>
#

'''
Restricted Open-shell Hartree-Fock
'''

from functools import reduce
import numpy
import pyscf.gto
from pyscf import lib
from pyscf.lib import logger
from pyscf.scf import hf
from pyscf.scf import uhf
import pyscf.scf.chkfile


def init_guess_by_minao(mol):
    dm = hf.init_guess_by_minao(mol)
    return numpy.array((dm*.5, dm*.5))

def init_guess_by_atom(mol):
    dm = hf.init_guess_by_atom(mol)
    return numpy.array((dm*.5, dm*.5))

init_guess_by_chkfile = uhf.init_guess_by_chkfile

def get_fock(mf, h1e=None, s1e=None, vhf=None, dm=None, cycle=-1, diis=None,
             diis_start_cycle=None, level_shift_factor=None, damp_factor=None):
    '''Build fock matrix based on Roothaan's effective fock.
    See also :func:`get_roothaan_fock`
    '''
    if h1e is None: h1e = mf.get_hcore()
    if vhf is None: vhf = mf.get_veff(dm=dm)
    if dm is None: dm = mf.make_rdm1()
    if isinstance(dm, numpy.ndarray) and dm.ndim == 2:
        dm = numpy.array((dm*.5, dm*.5))
# To Get orbital energy in get_occ, we saved alpha and beta fock, because
# Roothaan effective Fock cannot provide correct orbital energy with `eig`
# TODO, check other treatment  J. Chem. Phys. 133, 141102
    focka = h1e + vhf[0]
    fockb = h1e + vhf[1]
    f = get_roothaan_fock((focka,fockb), dm, s1e)
    if cycle < 0 and diis is None:  # Not inside the SCF iteration
        return f

    if diis_start_cycle is None:
        diis_start_cycle = mf.diis_start_cycle
    if level_shift_factor is None:
        level_shift_factor = mf.level_shift
    if damp_factor is None:
        damp_factor = mf.damp

    dm_tot = dm[0] + dm[1]
    if 0 <= cycle < diis_start_cycle-1 and abs(damp_factor) > 1e-4:
        raise NotImplementedError('ROHF Fock-damping')
    if diis and cycle >= diis_start_cycle:
        f = diis.update(s1e, dm_tot, f, mf, h1e, vhf)
    f = hf.level_shift(s1e, dm_tot*.5, f, level_shift_factor)
    return f

def get_roothaan_fock(focka_fockb, dma_dmb, s):
    '''Roothaan's effective fock.
    Ref. http://www-theor.ch.cam.ac.uk/people/ross/thesis/node15.html

    ======== ======== ====== =========
    space     closed   open   virtual
    ======== ======== ====== =========
    closed      Fc      Fb     Fc
    open        Fb      Fc     Fa
    virtual     Fc      Fa     Fc
    ======== ======== ====== =========

    where Fc = (Fa + Fb) / 2

    Returns:
        Roothaan effective Fock matrix
    '''
    nao = s.shape[0]
    focka, fockb = focka_fockb
    dma, dmb = dma_dmb
    fc = (focka + fockb) * .5
# Projector for core, open-shell, and virtual
    pc = numpy.dot(dmb, s)
    po = numpy.dot(dma-dmb, s)
    pv = numpy.eye(nao) - numpy.dot(dma, s)
    fock  = reduce(numpy.dot, (pc.T, fc, pc)) * .5
    fock += reduce(numpy.dot, (po.T, fc, po)) * .5
    fock += reduce(numpy.dot, (pv.T, fc, pv)) * .5
    fock += reduce(numpy.dot, (po.T, fockb, pc))
    fock += reduce(numpy.dot, (po.T, focka, pv))
    fock += reduce(numpy.dot, (pv.T, fc, pc))
    fock = fock + fock.T
    fock = lib.tag_array(fock, focka=focka, fockb=fockb)
    return fock


def get_occ(mf, mo_energy=None, mo_coeff=None):
    '''Label the occupancies for each orbital.
    NOTE the occupancies are not assigned based on the orbital energy ordering.
    The first N orbitals are assigned to be occupied orbitals.

    Examples:

    >>> mol = gto.M(atom='H 0 0 0; O 0 0 1.1', spin=1)
    >>> mf = scf.hf.SCF(mol)
    >>> energy = numpy.array([-10., -1., 1, -2., 0, -3])
    >>> mf.get_occ(energy)
    array([2, 2, 2, 2, 1, 0])
    '''

    if mo_energy is None: mo_energy = mf.mo_energy
    if hasattr(mo_energy, 'mo_ea'):
        mo_ea = mo_energy.mo_ea
        mo_eb = mo_energy.mo_eb
    else:
        mo_ea = mo_eb = mo_energy
    nmo = mo_ea.size
    mo_occ = numpy.zeros(nmo)
    if mf.nelec is None:
        nelec = mf.mol.nelec
    else:
        nelec = mf.nelec
    ncore = nelec[1]
    nocc  = nelec[0]
    nopen = nocc - ncore
    mo_occ = _fill_rohf_occ(mo_energy, mo_ea, mo_eb, ncore, nopen)

    if mf.verbose >= logger.INFO and nocc < nmo and ncore > 0:
        ehomo = max(mo_energy[mo_occ> 0])
        elumo = min(mo_energy[mo_occ==0])
        if ehomo+1e-3 > elumo:
            logger.warn(mf.mol, 'HOMO %.15g >= LUMO %.15g',
                        ehomo, elumo)
        else:
            logger.info(mf, '  HOMO = %.15g  LUMO = %.15g',
                        ehomo, elumo)
        if nopen > 0:
            core_idx = mo_occ == 2
            open_idx = mo_occ == 1
            vir_idx = mo_occ == 0
            logger.debug(mf, '                  Roothaan           | alpha              | beta')
            logger.debug(mf, '  Highest 2-occ = %18.15g | %18.15g | %18.15g',
                         max(mo_energy[core_idx]),
                         max(mo_ea[core_idx]), max(mo_eb[core_idx]))
            logger.debug(mf, '  Lowest 0-occ =  %18.15g | %18.15g | %18.15g',
                         min(mo_energy[vir_idx]),
                         min(mo_ea[vir_idx]), min(mo_eb[vir_idx]))
            for i in numpy.where(open_idx)[0]:
                logger.debug(mf, '  1-occ =         %18.15g | %18.15g | %18.15g',
                             mo_energy[i], mo_ea[i], mo_eb[i])

        numpy.set_printoptions(threshold=nmo)
        logger.debug(mf, '  Roothaan mo_energy =\n%s', mo_energy)
        logger.debug1(mf, '  alpha mo_energy =\n%s', mo_ea)
        logger.debug1(mf, '  beta  mo_energy =\n%s', mo_eb)
        numpy.set_printoptions(threshold=1000)
    return mo_occ

def _fill_rohf_occ(mo_energy, mo_energy_a, mo_energy_b, ncore, nopen):
    mo_occ = numpy.zeros_like(mo_energy)
    open_idx = []
    try:
        core_sort = numpy.argpartition(mo_energy, ncore-1)
        core_idx = core_sort[:ncore]
        if nopen > 0:
            open_idx = core_sort[ncore:]
# Fill up open shell based on alpha orbital energy
            open_sort = numpy.argpartition(mo_energy_a[open_idx], nopen-1)
            open_idx = open_idx[open_sort[:nopen]]
    except AttributeError:
        core_sort = numpy.argsort(mo_energy)
        core_idx = core_sort[:ncore]
        if nopen > 0:
            open_idx = core_sort[ncore:]
            open_sort = numpy.argsort(mo_energy_a[open_idx])
            open_idx = open_idx[open_sort[:nopen]]
    mo_occ[core_idx] = 2
    mo_occ[open_idx] = 1
    return mo_occ

def get_grad(mo_coeff, mo_occ, fock):
    '''ROHF gradients is the off-diagonal block [co + cv + ov], where
    [ cc co cv ]
    [ oc oo ov ]
    [ vc vo vv ]
    '''
    occidxa = mo_occ > 0
    occidxb = mo_occ == 2
    viridxa = ~occidxa
    viridxb = ~occidxb
    uniq_var_a = viridxa.reshape(-1,1) & occidxa
    uniq_var_b = viridxb.reshape(-1,1) & occidxb

    if hasattr(fock, 'focka'):
        focka = fock.focka
        fockb = fock.fockb
    elif fock.ndim == 3:
        focka, fockb = fock
    else:
        focka = fockb = fock
    focka = reduce(numpy.dot, (mo_coeff.T.conj(), focka, mo_coeff))
    fockb = reduce(numpy.dot, (mo_coeff.T.conj(), fockb, mo_coeff))

    g = numpy.zeros_like(focka)
    g[uniq_var_a]  = focka[uniq_var_a]
    g[uniq_var_b] += fockb[uniq_var_b]
    return g[uniq_var_a | uniq_var_b]

def make_rdm1(mo_coeff, mo_occ):
    '''One-particle densit matrix.  mo_occ is a 1D array, with occupancy 1 or 2.
    '''
    mo_a = mo_coeff[:,mo_occ>0]
    mo_b = mo_coeff[:,mo_occ==2]
    dm_a = numpy.dot(mo_a, mo_a.T)
    dm_b = numpy.dot(mo_b, mo_b.T)
    return numpy.array((dm_a, dm_b))

def energy_elec(mf, dm=None, h1e=None, vhf=None):
    if dm is None: dm = mf.make_rdm1()
    elif isinstance(dm, numpy.ndarray) and dm.ndim == 2:
        dm = numpy.array((dm*.5, dm*.5))
    ee, ecoul = uhf.energy_elec(mf, dm, h1e, vhf)
    logger.debug(mf, 'Ecoul = %.15g', ecoul)
    return ee, ecoul

# pass in a set of density matrix in dm as (alpha,alpha,...,beta,beta,...)
def get_veff(mol, dm, dm_last=0, vhf_last=0, hermi=1, vhfopt=None):
    return uhf.get_veff(mol, dm, dm_last, vhf_last, hermi, vhfopt)

def analyze(mf, verbose=logger.DEBUG, with_meta_lowdin=True, **kwargs):
    '''Analyze the given SCF object:  print orbital energies, occupancies;
    print orbital coefficients; Mulliken population analysis
    '''
    from pyscf.lo import orth
    from pyscf.tools import dump_mat
    mo_energy = mf.mo_energy
    mo_occ = mf.mo_occ
    mo_coeff = mf.mo_coeff
    log = logger.new_logger(mf, verbose)
    if log.verbose >= logger.NOTE:
        log.note('**** MO energy ****')
        if hasattr(mo_energy, 'mo_ea'):
            mo_ea = mo_energy.mo_ea
            mo_eb = mo_energy.mo_eb
            log.note('                Roothaan           | alpha              | beta')
            for i,c in enumerate(mo_occ):
                log.note('MO #%-3d energy= %-18.15g | %-18.15g | %-18.15g occ= %g',
                         i+1, mo_energy[i], mo_ea[i], mo_eb[i], c)
        else:
            for i,c in enumerate(mo_occ):
                log.note('MO #%-3d energy= %-18.15g occ= %g', i+1, mo_energy[i], c)

    ovlp_ao = mf.get_ovlp()
    if log.verbose >= logger.DEBUG:
        label = mf.mol.ao_labels()
        if with_meta_lowdin:
            log.debug(' ** MO coefficients (expansion on meta-Lowdin AOs) **')
            orth_coeff = orth.orth_ao(mf.mol, 'meta_lowdin', s=ovlp_ao)
            c = reduce(numpy.dot, (orth_coeff.T, ovlp_ao, mo_coeff))
        else:
            log.debug(' ** MO coefficients (expansion on AOs) **')
            c = mo_coeff
        dump_mat.dump_rec(mf.stdout, c, label, start=1, **kwargs)
    dm = mf.make_rdm1(mo_coeff, mo_occ)
    if with_meta_lowdin:
        return mf.mulliken_meta(mf.mol, dm, s=ovlp_ao, verbose=log)
    else:
        return mf.mulliken_pop(mf.mol, dm, s=ovlp_ao, verbose=log)

def canonicalize(mf, mo_coeff, mo_occ, fock=None):
    '''Canonicalization diagonalizes the Fock matrix within occupied, open,
    virtual subspaces separatedly (without change occupancy).
    '''
    if not hasattr(fock, 'focka'):
        dm = mf.make_rdm1(mo_coeff, mo_occ)
        fock = mf.get_fock(dm=dm)
    mo_e, mo_coeff = hf.canonicalize(mf, mo_coeff, mo_occ, fock)
    mo_ea = numpy.einsum('pi,pi->i', mo_coeff, fock.focka.dot(mo_coeff))
    mo_eb = numpy.einsum('pi,pi->i', mo_coeff, fock.fockb.dot(mo_coeff))
    mo_e = lib.tag_array(mo_e, mo_ea=mo_ea, mo_eb=mo_eb)
    return mo_e, mo_coeff

# use UHF init_guess, get_veff, diis, and intermediates such as fock, vhf, dm
# keep mo_energy, mo_coeff, mo_occ as RHF structure

class ROHF(hf.RHF):
    __doc__ = hf.SCF.__doc__

    def __init__(self, mol):
        hf.SCF.__init__(self, mol)
        self.nelec = None
        self._keys = self._keys.union(['nelec'])

    def dump_flags(self):
        hf.SCF.dump_flags(self)
        if hasattr(self, 'nelectron_alpha'):
            logger.warn(self, 'Note the API updates: attribute nelectron_alpha was replaced by attribute nelec')
            #raise RuntimeError('API updates')
            self.nelec = (self.nelectron_alpha,
                          self.mol.nelectron-self.nelectron_alpha)
            delattr(self, 'nelectron_alpha')
        if self.nelec is None:
            nelec = self.mol.nelec
        else:
            nelec = self.nelec
        logger.info(self, 'num. doubly occ = %d  num. singly occ = %d',
                    nelec[1], nelec[0]-nelec[1])

    def init_guess_by_minao(self, mol=None):
        if mol is None: mol = self.mol
        return init_guess_by_minao(mol)

    def init_guess_by_atom(self, mol=None):
        if mol is None: mol = self.mol
        logger.info(self, 'Initial guess from superpostion of atomic densties.')
        return init_guess_by_atom(mol)

    def init_guess_by_1e(self, mol=None):
        if mol is None: mol = self.mol
        logger.info(self, 'Initial guess from hcore.')
        h1e = self.get_hcore(mol)
        s1e = self.get_ovlp(mol)
        mo_energy, mo_coeff = self.eig(h1e, s1e)
        mo_occ = self.get_occ(mo_energy, mo_coeff)
        return self.make_rdm1(mo_coeff, mo_occ)

    def init_guess_by_chkfile(self, chkfile=None, project=True):
        if chkfile is None: chkfile = self.chkfile
        return init_guess_by_chkfile(self.mol, chkfile, project=project)

    get_fock = get_fock
    get_occ = get_occ

    @lib.with_doc(hf.eig.__doc__)
    def eig(self, fock, s):
        e, c = self._eigh(fock, s)
        if hasattr(fock, 'focka'):
            mo_ea = numpy.einsum('pi,pi->i', c, fock.focka.dot(c))
            mo_eb = numpy.einsum('pi,pi->i', c, fock.fockb.dot(c))
            e = lib.tag_array(e, mo_ea=mo_ea, mo_eb=mo_eb)
        return e, c

    @lib.with_doc(get_grad.__doc__)
    def get_grad(self, mo_coeff, mo_occ, fock=None):
        if fock is None:
            dm1 = self.make_rdm1(mo_coeff, mo_occ)
            fock = self.get_hcore(self.mol) + self.get_veff(self.mol, dm1)
        return get_grad(mo_coeff, mo_occ, fock)

    @lib.with_doc(make_rdm1.__doc__)
    def make_rdm1(self, mo_coeff=None, mo_occ=None):
        if mo_coeff is None: mo_coeff = self.mo_coeff
        if mo_occ is None: mo_occ = self.mo_occ
        return make_rdm1(mo_coeff, mo_occ)

    energy_elec = energy_elec

    @lib.with_doc(uhf.get_veff.__doc__)
    def get_veff(self, mol=None, dm=None, dm_last=0, vhf_last=0, hermi=1):
        if mol is None: mol = self.mol
        if dm is None: dm = self.make_rdm1()
        if isinstance(dm, numpy.ndarray) and dm.ndim == 2:
            dm = numpy.array((dm*.5, dm*.5))
        if (self._eri is not None or not self.direct_scf or
            mol.incore_anyway or self._is_mem_enough()):
            vj, vk = self.get_jk(mol, dm, hermi)
            vhf = uhf._makevhf(vj, vk)
        else:
            ddm = dm - numpy.asarray(dm_last)
            vj, vk = self.get_jk(mol, ddm, hermi)
            vhf = uhf._makevhf(vj, vk) + numpy.asarray(vhf_last)
        return vhf

    @lib.with_doc(analyze.__doc__)
    def analyze(self, verbose=None, with_meta_lowdin=True, **kwargs):
        if verbose is None: verbose = self.verbose
        return analyze(self, verbose, with_meta_lowdin, **kwargs)

    canonicalize = canonicalize

    def stability(self, internal=True, external=False, verbose=None):
        from pyscf.scf.stability import rohf_stability
        return rohf_stability(self, internal, external, verbose)


class HF1e(ROHF):
    def scf(self, *args):
        logger.info(self, '\n')
        logger.info(self, '******** 1 electron system ********')
        self.converged = True
        h1e = self.get_hcore(self.mol)
        s1e = self.get_ovlp(self.mol)
        self.mo_energy, self.mo_coeff = self.eig(h1e, s1e)
        self.mo_occ = self.get_occ(self.mo_energy, self.mo_coeff)
        self.e_tot = self.mo_energy[self.mo_occ>0][0] + self.mol.energy_nuc()
        self._finalize()
        return self.e_tot

