'''
Created on Jan 23, 2015

@author: danieles
'''

import re

from sympy import sympify
from islpy import Set, Map, format, Context, Space, align_spaces, Constraint, Aff, PwAff, dim_type

from src.dsls.ll import Assign, Matrix, ConstantMatrix, AllEntriesConstantMatrix, ZeroMatrix, Triangular, Sqrt, Add, Sub, Neg, Mul, LDiv, Div, T, Kro, G, S, HRed, PMul, Index, fHbs, globalSSAIndex,\
    scalar_block, Quantity, Tile, LowerTriangular, UpperTriangular, llBlock, llFor, llIf, llStmt
from src.dsls.sigmall import sllProgram, parseSigmaLL, Sum
from src.dsls.processing import reorderIdxList
from copy import deepcopy



def rewriteToSigma_old(llprog, opts):
#     rew = ToSigma()
    rew = ToPolySigma(llprog)
    sllprog = sllProgram()
    for s in llprog.stmtList:
        sllprog.extend( rew.apply(s.eq, opts) )
    return sllprog

def rewriteToSigma(llprog, opts):
    rew = ToPolySigma(llprog, opts)
    sllprog = sllProgram(rew.apply())
    return sllprog

#-------------------- LL -> Sigma-LL ---------------------

class ToSigma(object):
    def __init__(self):
        super(ToSigma, self).__init__()
    
    def apply(self, root, opts):
        return getattr(self, root.__class__.__name__)(root, opts)
    
    def Assign(self, expr, opts):
        lhs = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        rhs = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts)

#        mLhs = lhs.getOut()
#        mRhs = rhs.getOut()
#        
#        if mLhs.attr['o']:
#            src = mRhs
#            dst = mLhs
#            sexpr = rhs
#        else:
#            src = mLhs
#            dst = mRhs
#            sexpr = lhs
#            
#        #Replace the PhysLayout of the destination with the one of the source
#        if not sexpr.reqAss and not dst.attr['i']:
#            srcPhys = ir.icode.bindingTable.getPhysicalLayout(src)
#            dstPhys = ir.icode.bindingTable.getPhysicalLayout(dst)
#            ir.icode.bindingTable.replaceConnectedPhysicalLayout(srcPhys, dstPhys, sexpr)
#            if not ir.icode.bindingTable.existPhysicalLayout(srcPhys):
#                ir.icode.declare.remove(srcPhys)
        
        return Assign(lhs, rhs) 
    
    def Tile(self, expr, opts):
        return getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)

    def Scalar(self, expr, opts):
        return self.Matrix(expr, opts)

    def SquaredMatrix(self, expr, opts):
        return self.Matrix(expr, opts)
    
    def LowerTriangular(self, expr, opts):
        return self.Matrix(expr, opts)
    
    def UpperTriangular(self, expr, opts):
        return self.Matrix(expr, opts)

    def Symmetric(self, expr, opts):
        return self.Matrix(expr, opts)

    def Matrix(self, expr, opts):
        sexpr = expr.duplicate()
        
#        if not sexpr.attr['o'] and sexpr.isScalar():
#             physLayout = Scalars(sexpr.name, sexpr.size, opts, isParam=True)
#        else:
#            physLayout = Array(sexpr.name, sexpr.size, opts, isOut=sexpr.attr['o'])
#        if ir.icode.bindingTable.addBinding(sexpr, physLayout):
#            ir.icode.signature += [physLayout]
        return sexpr
    
    def T(self, expr, opts): 
        sub = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        
        subOut = sub.getOut()
        if subOut.isScalar():
            return sub
        

        blk = expr.getOut()
        M,N = sympify(blk.size[0]), sympify(blk.size[1])
        topSize = blk.getPartitionSize(0,0)
        SI,SJ = sympify(topSize[0]), sympify(topSize[1])
        I,J = Index("I", sympify(0), M, SI, True), Index("J", sympify(0), N, SJ, True)
        idxList = [I,J]
        uFactors = [sympify(2)]*2
        iPriority = { I.i: {'t': 0, 's': 0, 'i': 0}, J.i:{'t': 0, 's': 0, 'i': 0} }
        flatM,flatN = sympify(blk.getFlatSize()[0]), sympify(blk.getFlatSize()[1])

        lev = 1
        bBlk, hBlk, vBlk = blk.getBlock(0,0), blk.getBlock(M-1,0), blk.getBlock(0,N-1)
        bFSize, hFSize, vFSize = sympify(bBlk.getFlatSize()), sympify(hBlk.getFlatSize()), sympify(vBlk.getFlatSize())
        iName, jName = "i"*lev, "j"*lev
        maxI, maxJ = SI*bFSize[0], SJ*bFSize[1]
        bi,ei,si = I.i*bFSize[0], maxI + I.i/SI*(flatM - maxI), bFSize[0] + I.i/SI*(hFSize[0] - bFSize[0])
        bj,ej,sj = J.i*bFSize[1], maxJ + J.i/SJ*(flatN - maxJ), bFSize[1] + J.i/SJ*(vFSize[1] - bFSize[1])
        i,j =  Index(iName, bi, ei, si), Index(jName, bj, ej, sj)
        idxList += [i,j]
        uFactors += [sympify(1),sympify(1)]
        iPriority.update({ i.i: {'t': lev, 's': 0, 'i': 0}, j.i:{'t': lev, 's': 0, 'i': 0} })
        l,r = fHbs(si,flatM,i.i,1), fHbs(sj,flatN,j.i,1)
        lev+=1

        baselevel = 2 if opts['useintrinsics'] else 1
        while bBlk.level > baselevel:
            bBlk, hBlk, vBlk = bBlk.getBlock(0,0), hBlk.getBlock(0,0), vBlk.getBlock(0,0)
            bFSize, hFSize, vFSize = bBlk.getFlatSize(), hBlk.getFlatSize(), vBlk.getFlatSize()
            iName, jName = "i"*lev, "j"*lev
            bi,ei,si = sympify(0), si, bFSize[0] + I.i/SI*(hFSize[0] - bFSize[0])
            bj,ej,sj = sympify(0), sj, bFSize[1] + J.i/SJ*(vFSize[1] - bFSize[1])
            i,j =  Index(iName, bi, ei, si), Index(jName, bj, ej, sj)
            idxList += [i,j]
            uFactors += [sympify(1),sympify(1)]
            iPriority.update({ i.i: {'t': lev, 's': 0, 'i': 0}, j.i:{'t': lev, 's': 0, 'i': 0} })
            l,r = l.compose(fHbs(si,ei,i.i,1)), r.compose(fHbs(sj,ej,j.i,1))
            lev+=1

        #Reorder ids based on priorities
        ordIdxList = reorderIdxList(idxList, iPriority, opts)
            
#        # Unroll inner loops
        if opts['unrollinner']:
            for i in range(len(ordIdxList)-2, len(ordIdxList)):
                uFactors[i] = ordIdxList[i].e - ordIdxList[i].b 

        
        gat = G(r, sub, l)
        sca = S(l, T(gat), r)
        
#        sexpr = Sum([ sca ], idxList, uFactors)
        sexpr = Sum([ sca ], ordIdxList, uFactors, outerIdx=[ I.i, J.i ], outDep=[ sca.fL.of(0), sca.fR.of(0) ], forceInitIdx=[ I.i, J.i ], iPriority=iPriority)
        
        return sexpr
        
        
    def Add(self, expr, opts):
        lhs = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        rhs = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts)
        
        #Accomodate arbitrary sizes by adding an outer loop to span across different homogeneous area of the matrix
#        lhsOut = lhs.getOut()
#        rhsOut = rhs.getOut()
        blk = expr.getOut()
        
        M,N = sympify(blk.size[0]), sympify(blk.size[1])
        topSize = blk.getPartitionSize(0,0)
        SI,SJ = sympify(topSize[0]), sympify(topSize[1])
        I,J = Index("I", sympify(0), M, SI, True), Index("J", sympify(0), N, SJ, True)
        idxList = [I,J]
        uFactors = [sympify(2)]*2
        iPriority = { I.i: {'t': 0, 's': 0, 'i': 0}, J.i:{'t': 0, 's': 1, 'i': 0} }
        flatM,flatN = sympify(blk.getFlatSize()[0]), sympify(blk.getFlatSize()[1])

        lev = 1
        bBlk, hBlk, vBlk = blk.getBlock(0,0), blk.getBlock(M-1,0), blk.getBlock(0,N-1)
        bFSize, hFSize, vFSize = sympify(bBlk.getFlatSize()), sympify(hBlk.getFlatSize()), sympify(vBlk.getFlatSize())
        iName, jName = "i"*lev, "j"*lev
        maxI, maxJ = SI*bFSize[0], SJ*bFSize[1]
        bi,ei,si = I.i*bFSize[0], maxI + I.i/SI*(flatM - maxI), bFSize[0] + I.i/SI*(hFSize[0] - bFSize[0])
        bj,ej,sj = J.i*bFSize[1], maxJ + J.i/SJ*(flatN - maxJ), bFSize[1] + J.i/SJ*(vFSize[1] - bFSize[1])
        i,j =  Index(iName, bi, ei, si), Index(jName, bj, ej, sj)
        idxList += [i,j]
        uFactors += [sympify(1),sympify(1)]
        iPriority.update({ i.i: {'t': lev, 's': 0, 'i': 0}, j.i:{'t': lev, 's': 1, 'i': 0} })
        l,r = fHbs(si,flatM,i.i,1), fHbs(sj,flatN,j.i,1)
        lev+=1
        
        baselevel = 2 if opts['useintrinsics'] else 1
        while bBlk.level > baselevel:
            bBlk, hBlk, vBlk = bBlk.getBlock(0,0), hBlk.getBlock(0,0), vBlk.getBlock(0,0)
            bFSize, hFSize, vFSize = bBlk.getFlatSize(), hBlk.getFlatSize(), vBlk.getFlatSize()
            iName, jName = "i"*lev, "j"*lev
            bi,ei,si = sympify(0), si, bFSize[0] + I.i/SI*(hFSize[0] - bFSize[0])
            bj,ej,sj = sympify(0), sj, bFSize[1] + J.i/SJ*(vFSize[1] - bFSize[1])
            i,j =  Index(iName, bi, ei, si), Index(jName, bj, ej, sj)
            idxList += [i,j]
            uFactors += [sympify(1),sympify(1)]
            iPriority.update({ i.i: {'t': lev, 's': 0, 'i': 0}, j.i:{'t': lev, 's': 1, 'i': 0} })
            l,r = l.compose(fHbs(si,ei,i.i,1)), r.compose(fHbs(sj,ej,j.i,1))
            lev+=1
        
        #Reorder ids based on priorities
        ordIdxList = reorderIdxList(idxList, iPriority, opts)
            
        # Unroll inner loops
        if opts['unrollinner']:
            for i in range(len(ordIdxList)-2, len(ordIdxList)):
                uFactors[i] = ordIdxList[i].e - ordIdxList[i].b 
#             uFactors[i] = sympify(2) 
#         uFactors[-1] = idxList[-1].e - idxList[-1].b 
#         uFactors[-1] = sympify(8)
        
        glhs = G(l, lhs, r)
        grhs = G(l, rhs, r)
        ssum = glhs + grhs
        ssca = S(l, ssum, r)
        sexpr = Sum([ ssca ], ordIdxList, uFactors, outerIdx=[ I.i, J.i ], outDep=[ ssca.fL.of(0), ssca.fR.of(0) ], forceInitIdx=[ I.i, J.i ], iPriority=iPriority)
    
        return sexpr

    def Kro(self, expr, opts): # Temporarily only dealing with sca-mat mul
        lhs = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        rhs = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts)
        
        lhsOut = lhs.getOut()
        rhsOut = rhs.getOut()
        sca,mat,scaOut,scaLhs = (lhs, rhs, lhsOut, True) if rhsOut.size[0]*rhsOut.size[1] > 1 else (rhs, lhs, rhsOut, False)
         
        blk = expr.getOut()

        M,N = sympify(blk.size[0]), sympify(blk.size[1])
        baselevel = 2 if opts['useintrinsics'] else 1
#         jSlocPrior = lambda lev: 0 if lev == baselevel else 2
#         ijIlpPrior = lambda lev: 1 if lev == baselevel else 0
        
        topSize = blk.getPartitionSize(0,0)
        SI,SJ = sympify(topSize[0]), sympify(topSize[1])
        I,J = Index("I", 0, M, SI, True), Index("J", 0, N, SJ, True)
        iPriority = { I.i: {'t': 0, 's': 0, 'i': 0}, J.i:{'t': 0, 's': 1, 'i': 0} }
        idxList = [I,J]
        uFactors = [sympify(2)]*2

        flatScaM,flatScaN = sympify(scaOut.getFlatSize()[0]), sympify(scaOut.getFlatSize()[1])
        flatM, flatN  = sympify(blk.getFlatSize()[0]), sympify(blk.getFlatSize()[1])
        flatMatM,flatMatN = flatM,flatN # For now rM == M and rN == N

        lev = 1
        bBlk, hBlk, vBlk = blk.getBlock(0,0), blk.getBlock(M-1,0), blk.getBlock(0,N-1)
        bFSize, hFSize, vFSize = sympify(bBlk.getFlatSize()), sympify(hBlk.getFlatSize()), sympify(vBlk.getFlatSize())
        iName, jName, kName, lName = "i", "j", "k", "l"
        maxI, maxJ = SI*bFSize[0], SJ*bFSize[1]
        bi,ei,si = 0, flatScaM, 1
        bj,ej,sj = 0, flatScaN, 1
        bk,ek,sk = I.i*bFSize[0], maxI + I.i/SI*(flatMatM - maxI), bFSize[0] + I.i/SI*(hFSize[0] - bFSize[0])
        bl,el,sl = J.i*bFSize[1], maxJ + J.i/SJ*(flatMatN - maxJ), bFSize[1] + J.i/SJ*(vFSize[1] - bFSize[1])
        i,j =  Index(iName, bi, ei, si), Index(jName, bj, ej, sj)
        k,l =  Index(kName, bk, ek, sk), Index(lName, bl, el, sl)
        idxList += [i,j,k,l]
        uFactors += [sympify(1),sympify(1),sympify(1),sympify(1)]
        iPriority.update({ i.i: {'t': lev, 's': 0, 'i': 0}, j.i:{'t': lev, 's': 1, 'i': 0} ,  k.i: {'t': lev, 's': 2, 'i': 0}, l.i:{'t': lev, 's': 3, 'i': 0} })
        ll,lr = fHbs(si,flatScaM,i.i,1), fHbs(sj,flatScaN,j.i,1)
        rl,rr = fHbs(sk,flatMatM,k.i,1), fHbs(sl,flatMatN,l.i,1)

        lev+=1
        
        while bBlk.level > baselevel:
            bBlk, hBlk, vBlk = bBlk.getBlock(0,0), hBlk.getBlock(0,0), vBlk.getBlock(0,0)
            bFSize, hFSize, vFSize = bBlk.getFlatSize(), hBlk.getFlatSize(), vBlk.getFlatSize()
            iName, jName = "i"*lev, "j"*lev
            kName, lName = "k"*lev, "l"*lev
            bi,ei,si = 0, si, 1
            bj,ej,sj = 0, sj, 1
            bk,ek,sk = 0, sk, bFSize[0] + I.i/SI*(hFSize[0] - bFSize[0])
            bl,el,sl = 0, sl, bFSize[1] + J.i/SJ*(vFSize[1] - bFSize[1])
            i,j =  Index(iName, bi, ei, si), Index(jName, bj, ej, sj)
            k,l =  Index(kName, bk, ek, sk), Index(lName, bl, el, sl)
            idxList += [i,j,k,l]
            uFactors += [sympify(1),sympify(1),sympify(1),sympify(1)]
            iPriority.update({ i.i: {'t': lev, 's': 0, 'i': 0}, j.i:{'t': lev, 's': 1, 'i': 0} ,  k.i: {'t': lev, 's': 2, 'i': 0}, l.i:{'t': lev, 's': 3, 'i': 0} })
            ll,lr = ll.compose(fHbs(si,ei,i.i,1)), lr.compose(fHbs(sj,ej,j.i,1))
            rl,rr = rl.compose(fHbs(sk,ek,k.i,1)), rr.compose(fHbs(sl,el,l.i,1))
            lev+=1
        
        #Reorder ids based on priorities
        ordIdxList = reorderIdxList(idxList, iPriority, opts)
            
        # Unroll inner loops
        if opts['unrollinner']:
            for i in range(len(ordIdxList)-2, len(ordIdxList)):
                uFactors[i] = ordIdxList[i].e - ordIdxList[i].b 
        
        gsca = G(ll, sca, lr)
        gmat = G(rl, mat, rr)
        if scaLhs:
#            smul = gsca * gmat
            smul = Kro(gsca, gmat)
        else:
#            smul = gmat * gsca
            smul = Kro(gmat, gsca)
        ssca = S(rl, smul, rr)
        sexpr = Sum([ ssca ], ordIdxList, uFactors, outerIdx=[ I.i, J.i ], outDep=[ ssca.fL.of(0), ssca.fR.of(0) ], forceInitIdx=[ I.i, J.i ], iPriority=iPriority)
    
        return sexpr
            
    def Mul(self, expr, opts):
        lhs = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        rhs = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts)
        
        #Accommodate arbitrary sizes by adding an outer loop to span across different homogeneous area of the matrix
#        lhsOut = lhs.getOut()
#        rhsOut = rhs.getOut()
        blkLhs = expr.getInexprMat(0)
        blkRhs = expr.getInexprMat(1)

        M,K,N = sympify(blkLhs.size[0]), sympify(blkLhs.size[1]), sympify(blkRhs.size[1])

        baselevel = 2 if opts['useintrinsics'] else 1
        kTlocPrior = lambda lev: 0 if lev == baselevel else 2 
        jSlocPrior = lambda lev: 0 if lev == baselevel else 2
        kSlocPrior = lambda lev: 0 if lev == baselevel else 1
        ijIlpPrior = lambda lev: 1 if lev == baselevel else 0
        
        topSizeLhs = blkLhs.getPartitionSize(0,0)
        topSizeRhs = blkRhs.getPartitionSize(0,0)

        SI,SK,SJ = sympify(topSizeLhs[0]), sympify(topSizeLhs[1]), sympify(topSizeRhs[1])

        I,iK,J = Index("I", sympify(0), M, SI, True), Index("K", sympify(0), K, SK, True), Index("J", sympify(0), N, SJ, True)

        idxList = [I,J,iK]
        uFactors = [sympify(2)]*3
        iPriority = { I.i: {'t': (0,0), 's': 0, 'i': 0}, J.i:{'t': (0,1), 's': 2, 'i': 0}, iK.i:{'t': (0,2), 's': 1, 'i': 0} }
        flatM,flatK,flatN = sympify(blkLhs.getFlatSize()[0]), sympify(blkLhs.getFlatSize()[1]), sympify(blkRhs.getFlatSize()[1])
        
        # mvm case for SSE - doesn't work well together with sumExchange in compiler.Compiler.generateKernel()
#         if flatN == 1 and opts['vectorize'] and SSE in opts['isa']:
        if False:
            return self.HRed(HRed(PMul(expr.inexpr[0], expr.inexpr[1], opts['nu'])), opts)
        else:
            lev = 1
            bLhs, hLhs, vLhs = blkLhs.getBlock(0,0), blkLhs.getBlock(M-1,0), blkLhs.getBlock(0,K-1)
            bLFSize, hLFSize, vLFSize = sympify(bLhs.getFlatSize()), sympify(hLhs.getFlatSize()), sympify(vLhs.getFlatSize())
            bRhs, vRhs = blkRhs.getBlock(0,0), blkRhs.getBlock(0,N-1)
            bRFSize, vRFSize = sympify(bRhs.getFlatSize()), sympify(vRhs.getFlatSize())
    
            iName, kName, jName = "i"*lev, "k"*lev, "j"*lev
            maxI, maxK, maxJ = SI*bLFSize[0], SK*bLFSize[1], SJ*bRFSize[1]
            bi,ei,si = I.i*bLFSize[0], maxI + I.i/SI*(flatM - maxI), bLFSize[0] + I.i/SI*(hLFSize[0] - bLFSize[0])
            bk,ek,sk = iK.i*bLFSize[1], maxK + iK.i/SK*(flatK - maxK), bLFSize[1] + iK.i/SK*(vLFSize[1] - bLFSize[1])
            bj,ej,sj = J.i*bRFSize[1], maxJ + J.i/SJ*(flatN - maxJ), bRFSize[1] + J.i/SJ*(vRFSize[1] - bRFSize[1])
    
            i,k,j =  Index(iName, bi, ei, si), Index(kName, bk, ek, sk), Index(jName, bj, ej, sj)
    
            idxList += [i,j,k]
            uFactors += [sympify(1),sympify(1),sympify(1)]
            iPriority.update({ i.i: {'t': (lev, 0), 's': 1, 'i': ijIlpPrior(bLhs.level)}, j.i:{'t': (lev, 1), 's': jSlocPrior(bLhs.level), 'i': ijIlpPrior(bLhs.level)} ,  k.i: {'t': (lev, kTlocPrior(bLhs.level)), 's': kSlocPrior(bLhs.level), 'i': 0} })
            fi,fk,fj = fHbs(si,flatM,i.i,1), fHbs(sk,flatK,k.i,1), fHbs(sj,flatN,j.i,1)
    
            lev+=1
            while bLhs.level > baselevel:
                bLhs, hLhs, vLhs = bLhs.getBlock(0,0), hLhs.getBlock(0,0), vLhs.getBlock(0,0)
                bLFSize, hLFSize, vLFSize = sympify(bLhs.getFlatSize()), sympify(hLhs.getFlatSize()), sympify(vLhs.getFlatSize())
                bRhs, vRhs = bRhs.getBlock(0,0), vRhs.getBlock(0,0)
                bRFSize, vRFSize = sympify(bRhs.getFlatSize()), sympify(vRhs.getFlatSize())
    
                iName, kName, jName = "i"*lev, "k"*lev, "j"*lev
                bi,ei,si = sympify(0), si, bLFSize[0] + I.i/SI*(hLFSize[0] - bLFSize[0])
                bk,ek,sk = sympify(0), sk, bLFSize[1] + iK.i/SK*(vLFSize[1] - bLFSize[1])
                bj,ej,sj = sympify(0), sj, bRFSize[1] + J.i/SJ*(vRFSize[1] - bRFSize[1])
                i,k,j =  Index(iName, bi, ei, si), Index(kName, bk, ek, sk), Index(jName, bj, ej, sj)
        
                idxList += [i,j,k]
                uFactors += [sympify(1),sympify(1),sympify(1)]
                iPriority.update({ i.i: {'t': (lev, 0), 's': 1, 'i': ijIlpPrior(bLhs.level)}, j.i:{'t': (lev, 1), 's': jSlocPrior(bLhs.level), 'i': ijIlpPrior(bLhs.level)} ,  k.i: {'t': (lev, kTlocPrior(bLhs.level)), 's': kSlocPrior(bLhs.level), 'i': 0} })
                fi,fk,fj = fi.compose(fHbs(si,ei,i.i,1)), fk.compose(fHbs(sk,ek,k.i,1)), fj.compose(fHbs(sj,ej,j.i,1))
                lev+=1
    
    #         # Changing order of the indices 
    #         innerk = idxList.pop()
    #         idxList.insert(len(idxList)-2, innerk)        
            #Reorder ids based on priorities
            ordIdxList = reorderIdxList(idxList, iPriority, opts)
                
            # Unrolling
            if opts['unrollinner']:
                for i in range(len(ordIdxList)-3, len(ordIdxList)):
                    uFactors[i] = ordIdxList[i].e - ordIdxList[i].b 
    #             uFactors[i] = sympify(8)
            
            glhs  = G(fi, lhs, fk)
            grhs  = G(fk, rhs, fj)
            smul0 = glhs * grhs
            ssca0 = S(fi, smul0, fj)
            
            acc=lhs.getOut().size[1] > bLhs.size[1] # Accumulation of products happens only when K > nu
            sexpr = Sum([ ssca0 ], ordIdxList, uFactors, acc=acc, outerIdx=[ I.i, J.i, iK.i ], outDep=[ ssca0.fL.of(0), ssca0.fR.of(0) ], forceInitIdx=[ I.i, J.i ], iPriority=iPriority)
    
            if acc: # This part can in principle be automated
                smul1 = glhs * grhs
                gTOut = G(fi, sexpr, fj)
                sadd  = gTOut + smul1 
                ssca1 = S(fi, sadd, fj)
                
                sexpr.inexpr.append(ssca1)
                sexpr.setAsPred()
            
        return sexpr
    
    def PMul(self, expr, opts):
        lhs = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        rhs = getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts)
        nu = expr.nu
        
        blkLhs = expr.getInexprMat(0)
        blkRhs = expr.getInexprMat(1)
        
        # get the size of the two matrix operands
        M,K,N = sympify(blkLhs.size[0]), sympify(blkLhs.size[1]), sympify(blkRhs.size[1])
        
        # level at which we stop creating sums
        baselevel = 2 if opts['useintrinsics'] else 1
        # index priority coefficients (Tloc -> temp. locality, Sloc -> spacial locality, Ilp -> instruction level parallelism)
        jSlocPrior = lambda lev: 0 if lev == baselevel else 2
        kSlocPrior = lambda lev: 1
        ijIlpPrior = lambda lev: 0
        
        # get the size of the main blocks of the two matrix operands
        topSizeLhs = blkLhs.getPartitionSize(0,0)
        topSizeRhs = blkRhs.getPartitionSize(0,0)
        # sympify the dimensions of the main blocks
        SI,SK,SJ = sympify(topSizeLhs[0]), sympify(topSizeLhs[1]), sympify(topSizeRhs[1])
        
        # create the indexes for the outer loop mentioned above
        I,iK,J = Index("I", sympify(0), M, SI, True), Index("K", sympify(0), K, SK, True), Index("J", sympify(0), N, SJ, True)

        idxList = [I,J,iK]
        # unrolling factor for each Index
        # in this case we want the outer loops fully unrolled (first iteration -> main block, second iteration -> leftover block)
        uFactors = [sympify(2)]*3
        iPriority = { I.i: {'t': (0,0), 's': 0, 'i': 0}, J.i:{'t': (0,1), 's': 2, 'i': 0}, iK.i:{'t': (0,2), 's': 1, 'i': 0} }
        # get the real sizes of the two matrix operands
        flatM,flatK,flatN = sympify(blkLhs.getFlatSize()[0]), sympify(blkLhs.getFlatSize()[1]), sympify(blkRhs.getFlatSize()[1])

        lev = 1
        # get topleft, bottom left and topright block of left operand and the corresponding block sizes
        bLhs, hLhs, vLhs = blkLhs.getBlock(0,0), blkLhs.getBlock(M-1,0), blkLhs.getBlock(0,K-1)
        bLFSize, hLFSize, vLFSize = sympify(bLhs.getFlatSize()), sympify(hLhs.getFlatSize()), sympify(vLhs.getFlatSize())
        # get topleft and topright block of right operand and the corresponding block sizes
        bRhs, vRhs = blkRhs.getBlock(0,0), blkRhs.getBlock(0,N-1)
        bRFSize, vRFSize = sympify(bRhs.getFlatSize()), sympify(vRhs.getFlatSize())
        
        # create the indexes for this level's loops
        iName, kName, jName = "i"*lev, "k"*lev, "j"*lev
        # these are the max flat values of i,j,k for the main block
        maxI, maxK, maxJ = SI*bLFSize[0], SK*bLFSize[1], SJ*bRFSize[1]
        # I.i/SI = 0 if we are in the main block / 1 if we are in the leftover block
        bi,ei,si = I.i*bLFSize[0], maxI + I.i/SI*(flatM - maxI), bLFSize[0] + I.i/SI*(hLFSize[0] - bLFSize[0])
        bk,ek,sk = iK.i*bLFSize[1], maxK + iK.i/SK*(flatK - maxK), bLFSize[1] + iK.i/SK*(vLFSize[1] - bLFSize[1])
        bj,ej,sj = J.i*bRFSize[1], maxJ + J.i/SJ*(flatN - maxJ), bRFSize[1] + J.i/SJ*(vRFSize[1] - bRFSize[1])
        i,k,j =  Index(iName, bi, ei, si), Index(kName, bk, ek, sk), Index(jName, bj, ej, sj)

        idxList += [i,j,k]
        uFactors += [sympify(1),sympify(1),sympify(1)]
        iPriority.update({ i.i: {'t': (lev, 0), 's': 1, 'i': ijIlpPrior(bLhs.level)}, j.i:{'t': (lev, 1), 's': jSlocPrior(bLhs.level), 'i': ijIlpPrior(bLhs.level)} ,  k.i: {'t': (lev, 2), 's': kSlocPrior(bLhs.level), 'i': 0} })
        fi,fk,fj = fHbs(si, flatM, i.i, 1), fHbs(sk, flatK, k.i, 1), fHbs(sj, flatN, j.i, 1)

        lev+=1
        while bLhs.level > baselevel: # don't go under the baselevel (2 for vectorized code)
            # all three blocks bLhs, hLhs, vLhs are homogeneous, so no need to worry about leftovers at this point
            bLhs, hLhs, vLhs = bLhs.getBlock(0,0), hLhs.getBlock(0,0), vLhs.getBlock(0,0)
            bLFSize, hLFSize, vLFSize = sympify(bLhs.getFlatSize()), sympify(hLhs.getFlatSize()), sympify(vLhs.getFlatSize())
            bRhs, vRhs = bRhs.getBlock(0,0), vRhs.getBlock(0,0)
            bRFSize, vRFSize = sympify(bRhs.getFlatSize()), sympify(vRhs.getFlatSize())

            iName, kName, jName = "i"*lev, "k"*lev, "j"*lev
            # the end values of the loops now are the step values of the immediately outer loops
            bi,ei,si = sympify(0), si, bLFSize[0] + I.i/SI*(hLFSize[0] - bLFSize[0])
            bk,ek,sk = sympify(0), sk, bLFSize[1] + iK.i/SK*(vLFSize[1] - bLFSize[1])
            bj,ej,sj = sympify(0), sj, bRFSize[1] + J.i/SJ*(vRFSize[1] - bRFSize[1])
            i,k,j =  Index(iName, bi, ei, si), Index(kName, bk, ek, sk), Index(jName, bj, ej, sj)
    
            idxList += [i,j,k]
            uFactors += [sympify(1),sympify(1),sympify(1)]
            iPriority.update({ i.i: {'t': (lev, 0), 's': 1, 'i': ijIlpPrior(bLhs.level)}, j.i:{'t': (lev, 1), 's': jSlocPrior(bLhs.level), 'i': ijIlpPrior(bLhs.level)} ,  k.i: {'t': (lev, 2), 's': kSlocPrior(bLhs.level), 'i': 0} })
            fi,fk,fj = fi.compose(fHbs(si,ei,i.i,1)), fk.compose(fHbs(sk,ek,k.i,1)), fj.compose(fHbs(sj,ej,j.i,1))
            lev+=1

        # reorder ids based on priorities
        ordIdxList = reorderIdxList(idxList, iPriority, opts)
            
        if opts['unrollinner']:
            # set unrolling factors of 3 innermost loops to the corresponding loop length in order to be eventually unrolled
            for i in range(len(ordIdxList)-3, len(ordIdxList)):
                uFactors[i] = ordIdxList[i].e - ordIdxList[i].b 
        
        fjsrc = fHbs(sj, sj, 0, 1)
        fjdst = fHbs(nu, nu, 0, 1)
        
        glhs  = G(fi, lhs, fk)
        grhs  = G(fk, rhs, fjsrc)
        smul0 = PMul(glhs, grhs, nu)
        ssca0 = S(fi, smul0, fjdst)
        
        acc = lhs.getOut().size[1] > bLhs.size[1] # Accumulation of products happens only when K > nu
        sexpr = Sum([ ssca0 ], ordIdxList, uFactors, acc=acc, outerIdx=[ I.i, J.i, iK.i ], outDep=[ ssca0.fL.of(0), ssca0.fR.of(0) ], forceInitIdx=[ I.i, J.i ], iPriority=iPriority)

        if acc:
            smul1 = PMul(glhs, grhs, nu)
            gTOut = G(fi, sexpr, fjdst)
            sadd  = gTOut + smul1 
            ssca1 = S(fi, sadd, fjdst)
            
            sexpr.inexpr.append(ssca1)
            sexpr.setAsPred()
        
        return sexpr
    
    def HRed(self, expr, opts):
        rhs = getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        mat = rhs
         
        blk = expr.getInexprMat(0)

        M,N = sympify(blk.size[0]), sympify(blk.size[1])
        baselevel = 2 if opts['useintrinsics'] else 1
        
        topSize = blk.getPartitionSize(0,0)
        SI,SJ = sympify(topSize[0]), sympify(topSize[1])
        I,J = Index("I", 0, M, SI, True), Index("J", 0, N, SJ, True)
        iPriority = { I.i: {'t': 0, 's': 0, 'i': 0}, J.i:{'t': 0, 's': 1, 'i': 0} }
        idxList = [I,J]
        uFactors = [sympify(2)]*2

        flatM, flatN  = sympify(blk.getFlatSize()[0]), sympify(blk.getFlatSize()[1])
        flatMatM,flatMatN = flatM,flatN

        lev = 1
        bBlk, hBlk, vBlk = blk.getBlock(0,0), blk.getBlock(M-1,0), blk.getBlock(0,N-1)
        bFSize, hFSize, vFSize = sympify(bBlk.getFlatSize()), sympify(hBlk.getFlatSize()), sympify(vBlk.getFlatSize())
        kName, lName = "i", "j"
        maxI, maxJ = SI*bFSize[0], SJ*bFSize[1]
        bk,ek,sk = I.i*bFSize[0], maxI + I.i/SI*(flatMatM - maxI), bFSize[0] + I.i/SI*(hFSize[0] - bFSize[0])
        bl,el,sl = J.i*bFSize[1], maxJ + J.i/SJ*(flatMatN - maxJ), bFSize[1] + J.i/SJ*(vFSize[1] - bFSize[1])
        k,l =  Index(kName, bk, ek, sk), Index(lName, bl, el, sl)
        idxList += [k,l]
        uFactors += [sympify(1),sympify(1)]
        iPriority.update({k.i: {'t': lev, 's': 2, 'i': 0}, l.i:{'t': lev, 's': 3, 'i': 0} })
        rl,rr = fHbs(sk,flatMatM,k.i,1), fHbs(sl,flatMatN,l.i,1)

        lev+=1
        
        while bBlk.level > baselevel:
            bBlk, hBlk, vBlk = bBlk.getBlock(0,0), hBlk.getBlock(0,0), vBlk.getBlock(0,0)
            bFSize, hFSize, vFSize = bBlk.getFlatSize(), hBlk.getFlatSize(), vBlk.getFlatSize()
            kName, lName = "i"*lev, "j"*lev
            bk,ek,sk = 0, sk, bFSize[0] + I.i/SI*(hFSize[0] - bFSize[0])
            bl,el,sl = 0, sl, bFSize[1] + J.i/SJ*(vFSize[1] - bFSize[1])
            k,l =  Index(kName, bk, ek, sk), Index(lName, bl, el, sl)
            idxList += [k,l]
            uFactors += [sympify(1),sympify(1)]
            iPriority.update({k.i: {'t': lev, 's': 2, 'i': 0}, l.i:{'t': lev, 's': 3, 'i': 0} })
            rl,rr = rl.compose(fHbs(sk,ek,k.i,1)), rr.compose(fHbs(sl,el,l.i,1))
            lev+=1
        
        #Reorder ids based on priorities
        ordIdxList = reorderIdxList(idxList, iPriority, opts)
            
        # Unroll inner loops
        if opts['unrollinner']:
            for i in range(len(ordIdxList)-2, len(ordIdxList)):
                uFactors[i] = ordIdxList[i].e - ordIdxList[i].b 
        
        fjdst = fHbs(1, 1, 0, 1)
        
        gmat = G(rl, mat, rr)
        hred = HRed(gmat)
        ssca = S(rl, hred, fjdst)
        sexpr = Sum([ ssca ], ordIdxList, uFactors, outerIdx=[ I.i, J.i ], outDep=[ ssca.fL.of(0), ssca.fR.of(0) ], forceInitIdx=[ I.i, J.i ], iPriority=iPriority)
    
        return sexpr
    
class StmtWrap(object):
    def __init__(self, wrap, inputs):
        self.wrap = wrap
        self.inputs = inputs
        
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        res = ""
        if len(self.wrap)<2:
            return res
        res += str(self.wrap[0])
        i = 0
        while i < len(self.inputs):
            res += str(self.inputs[i])
            res += str(self.wrap[1+i])
            i+=1
        return res

class StmtExpr(object):
    def __init__(self, inputs, op=None, wrap=None):
        self.inputs = inputs
        self.op = op
        self.wrap = ["",""] if wrap is None else wrap

    def removeWrap(self):
        self.wrap = ["",""]
        return self

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        res = ""
        if len(self.inputs) > 1:
            res = str(self.inputs[0]) + self.op.toPolySigma() + str(self.inputs[1])
        else:
            if self.op is None:
                res = str(self.inputs[0])
            else:
                res = self.op.toPolySigma() + "(" + str(self.inputs[0]) + ")"
        w0, w1 = str(self.wrap[0]), str(self.wrap[1])
        if w0+w1 != "":
            if w0+w1 == "()":
                w0 = w1 = '' 
            res = w0 + "(" + res + ")" + w1 
#         res = str(self.wrap[0]) + "(" + res + ")" + str(self.wrap[1]) 
        return res
    
class ToPolySigma(object):
    
    def __init__(self, llprog, opts):
        super(ToPolySigma, self).__init__()
        self.mDict = dict(llprog.mDict)
        self.ops = llprog.getOps()
        self.llprog = llprog
        self.opts = opts
        
#     def apply(self, root, opts):
    def apply(self):
        self.eq_id = 0
        self.numStmts = 0
        self.stmts = []
        self.globalspace = None
        self.indices = []
        self.idxPriorityList = []
#         self.globIdxOrder = []
        self.subsWithOut = {}
        self.sigmaSource = ""
        
        self.nublac = self.opts['isaman'].getNuBLAC(self.opts['precision'], self.opts['nu'])
        
        self.baselevel = 3 if self.opts['useintrinsics'] else 2 # Mat level
#         if 'baseufs' not in self.opts: 
        self.opts['baseufs'] = { }
        if 'unroll' not in self.opts: 
            self.opts['unroll'] = { }
        self.opts['ufslist'] = [ ]  # Currently unused
#OLD        
#         self.fillinSubsWithOut(root, opts)
#         self.computeOpenSCoPSpace(root, opts)
#         self.computeSumsOrderAndUnrolling(root, opts)
#         self.opOrder = 0
#         getattr(self, root.__class__.__name__)(root, opts)
#         self.correctDomains(root.getPolyStmts())
#         self.computeScheds(root)
#         self.addStmts(root.getPolyStmts())

#NEW
        print "Computing OpenSCoP space.."
        self.computeOpenSCoPSpace()
        print "Computing indices pos e levels.."
        for eq_id, root in enumerate( self.llprog.getEqsList() ):
            root.computeIdxPosAndLevInfo()
            self.fillinSubsWithOut(eq_id, root)
#         self.opOrder = 0
        print "Starting polystatements computation.."
        getattr(self, self.llprog.__class__.__name__)(self.llprog)
        print "Fixing polystatements.."
        self.fix_ps_choice(self.llprog.stmtList)
        print "Ended polystatements computation.."
        self.opts['stmts_ids'] = { }
        print "Computing local sums and order.."
        self.computeLocalSumsOrder(self.llprog.stmtList)
        print "Computing Unrolling properties.."
        self.computeUnrollingAndProperties()
        
        self.scat_counter = -1
        self.scatnames = []
        print "Computing Scatnames expression tree.."
        self.computeScatNamesExprTree(self.llprog.stmtList, 0)
        print "Adding indices from polystatements.."
        self.computeScatNamesAddStmtsIds(self.llprog.stmtList)
#         self.computeSumsOrderAndUnrolling(root, opts)
        print "Computing schedules.."
        self.computeScheds(self.llprog.stmtList)

        print "Compiling CLooG statements.."
        for root in self.llprog.getEqsList():
            self.addStmts(root.getPolyStmts())

        print "Completing CLooG input.."
        self.createOpenSCoP()
        print "Creating Sigma-LL source.."
        self.createSigmaSource()
        if not self.opts.get('onlygen', False) and self.opts.get('savesigma', False):
            params = '-'.join(str(p) for p in self.opts['static_params'])
            destfile = '/%s_sigma-%s-%s.txt' % (self.opts['hfilebasename'], params, str(hash(self.llprog)))
            fname = self.opts['logroot'] + '/results/' + self.opts['testname'] + destfile 
            sigmasrc  = open(fname, 'w')
            sigmasrc.write("Sigma-LL src for :\n\n")        
            sigmasrc.write(str(self.llprog) + "\n\n")        
            sigmasrc.write("="*20 + "\n\n")        
            sigmasrc.write(self.sigmaSource + "\n\n")        
            sigmasrc.write("="*20 + "\n\n")        
            sigmasrc.close()
        self.opts['stmts_ids'].clear()
        print "Parsing new Sigma-LL input.."
        sem = parseSigmaLL(self.sigmaSource, self.mDict, self.opts, {'indices': self.indices} )
        print "Parsing concluded."
        return sem
    
    def fillinSubsWithOut(self, eq_id, root):
        self.subsWithOut[ (eq_id, root.inexpr[1]) ] = root.inexpr[0]

    def getEmptyDomain(self):
        emp = Set.universe(self.globalspace)
        return emp-emp

    def fix_ps_choice(self, expr):
        if isinstance(expr, llBlock):
            for s in expr:
                self.fix_ps_choice(s)
        elif isinstance(expr, llFor):
            self.fix_ps_choice(expr.body)
        elif isinstance(expr, llStmt):
            for ps in expr.eq.getPolyStmts():
                stmts_no_perm = filter(lambda t: t[1] is None, zip(ps['stmt'], ps['perm_oacc'], ps['domain'], ps['outinfo']))
                #If any choice with no perm required exists take it otherwise peek first choice
                if stmts_no_perm:
                    ps['stmt'], ps['perm_oacc'], ps['domain'], ps['outinfo'] = stmts_no_perm[0]
                else:
                    for f in ['stmt','perm_oacc','domain','outinfo']:
                        ps[f] = ps[f][0]
        elif isinstance(expr, llIf):
            for b in expr.bodys:
                self.fix_ps_choice(b)
        
#     def computeOpenSCoPSpace(self, root, opts):
    def computeOpenSCoPSpace(self):
        self.opts['idsattr'] = {}
#         root.computeSpaceIdxNames(i='i',j='j', ipfix=str(globalSSAIndex()), jpfix=str(globalSSAIndex()), opts=opts, baselevel=self.baselevel)
#         l = [root]
        self.llprog.computeSpaceIdxNames(opts=self.opts, baselevel=self.baselevel)
#         l = self.llprog.getEqsList()
#         while l:
#             tl = []
#             for e in l:
#                 for ids in e.getOut().spaceIdxNames:
#                     for c in range(len(ids)):
#                         prefix = self.opts['idsattr'].get(ids[c][0], None)
#                         if prefix:
#                             ids[c] = prefix + ids[c]
#                 if isinstance(e, Operator):
#                     tl += e.inexpr
#             l = tl
        self.indices = list(self.llprog.getSpaceIdxSet())
        self.globalspace = Space.create_from_names(Context(), set=self.indices)

    def computeSumsOrder(self, iPriorityList, ids):
#     def computeGlobalOrder(self):
#         self.globIdxOrder = []
        globIdxPriority = {}
        for i in ids:
            maxValue = (0,0,0)
            for ip in iPriorityList:
                if ip[i] > maxValue:
                    maxValue = ip[i]
            globIdxPriority[i] = maxValue
        ordPrioList = sorted(globIdxPriority.items(), key=lambda idxp: idxp[1])
        ordSym = [ idxp[0] for idxp in ordPrioList ]
        globIdxOrder = [None]*len(ids)
        for idx in ids:
            globIdxOrder[ordSym.index(idx)] = idx
        return globIdxOrder 

    
    def computeLocalSumsOrder(self, expr):
        if isinstance(expr, llBlock):
            for s in expr:
                self.computeLocalSumsOrder(s)
        elif isinstance(expr, llFor):
            self.computeLocalSumsOrder(expr.body)
        elif isinstance(expr, llStmt):
            iPriorityList = []
            ids = list(expr.getSpaceIdxSet())
            baselevel =  self.baselevel if expr.can_gen_with_nublac(self.nublac) else 2
            expr.eq.computeIdxPriority(iPriorityList, ids, self.opts['indexorder'], baselevel)
            self.opts['stmts_ids'][expr] = self.computeSumsOrder(iPriorityList, ids)
        elif isinstance(expr, llIf):
            for b in expr.bodys:
                self.computeLocalSumsOrder(b)
#     def computeSumsOrderAndUnrolling(self):
#         root.computeIdxPriority(self.idxPriorityList, self.indices, opts['indexorder'], self.baselevel)
#         self.computeGlobalOrder()

    def computeUnrollingAndProperties(self):
        baseUFs = { i : 1 for i in self.indices }
#         opts['baseufs'] = baseUFs
#         opts['ufslist'] = [ ]
        self.opts['baseufs'].update(baseUFs)
#         unroll = 1 if self.ops <= self.opts['icachel1'] else 0
#         uFs = { i : [unroll] for i in self.indices } # Using uFs only to mark whether we wnat to unroll over a specific dimension
        unroll = self.ops <= self.opts['icachel1']
        for stmt in self.opts['stmts_ids']:
#             ids = self.opts['stmts_ids'][stmt]
            baselevel =  self.baselevel if stmt.can_gen_with_nublac(self.nublac) else 2
            uFs = { i : [0] for i in self.indices }
            if unroll: 
                stmt.eq.computeUnrolling(uFs, self.indices, baselevel)
    #         opts['unroll'] = { i : max(uFs[i]) for i in self.indices }
            self.opts['unroll'].update( { i : max(uFs[i]) for i in self.indices } )
           
            propDict = {i : set() for i in self.indices }
            isRowIdx = lambda idx, idxInfoList, baselevel: any(map(lambda idxInfo: idx in idxInfo and idxInfo[idx][2] == 0, idxInfoList))
            isColIdx = lambda idx, idxInfoList, baselevel: any(map(lambda idxInfo: idx in idxInfo and idxInfo[idx][2] == 1, idxInfoList))
            canDistributeOverIdx = lambda op, idx, idxInfoList, baselevel: 'dist' if isinstance(op, Mul) and isRowIdx(idx, idxInfoList, baselevel) and isColIdx(idx, idxInfoList, baselevel) else None
            propList = [ canDistributeOverIdx ]
            stmt.eq.markProperties(propDict, propList, self.indices, baselevel)
            self.opts['idxProperties'] = propDict
#         uFs = { i : [1] for i in self.indices }
#         root.computeUnrolling(uFs, self.indices, self.baselevel)
#         uFs = { i : max(uFs[i]) for i in self.indices }
#         if uFs != baseUFs:
#             for uf in range(2,4):
#                 t = { i : uf if uFs[i] > 1 else 1 for i in uFs }
#                 opts['ufslist'].append(t)

    def computeScatNamesExprTree(self, expr, level):
        if isinstance(expr, llBlock):
            if level+1 > len(self.scatnames):
                self.scat_counter += 1
                self.scatnames.append( "b"+str(self.scat_counter) )
            for s in expr:
                self.computeScatNamesExprTree(s, level + 1)
        elif isinstance(expr, llFor):
            if level+1 > len(self.scatnames):
                self.scat_counter += 1
                self.scatnames.append(str(expr.idx))
            self.computeScatNamesExprTree(expr.body, level + 1)
        elif isinstance(expr, llIf):
            for b in expr.bodys:
                self.computeScatNamesExprTree(b, level)
            
#         elif isinstance(expr, llStmt):
#             res = list(self.opts['stmts_ids'][expr])

    def computeScatNamesAddStmtsIds(self, expr):
        if isinstance(expr, llBlock):
            for s in expr:
                self.computeScatNamesAddStmtsIds(s)
        elif isinstance(expr, llFor):
            self.computeScatNamesAddStmtsIds(expr.body)
        elif isinstance(expr, llStmt):
            self.scatnames.extend( list(self.opts['stmts_ids'][expr]) )
        elif isinstance(expr, llIf):
            for b in expr.bodys:
                self.computeScatNamesAddStmtsIds(b)
        
    def joinAlignedSets(self, set1, set2, space):
        lBsets1,lBsets2 = set1.get_basic_sets(), set2.get_basic_sets()
        genpair = ((bs1,bs2) for bs1 in lBsets1 for bs2 in lBsets2)
        set3 = Set.universe(space)
        set3 = set3-set3
        for bs1,bs2 in genpair:
            tempd = Set.universe(space)
            cs = bs1.get_constraints() + bs2.get_constraints()
            tempd = tempd.add_constraints(cs)
            set3 = set3.union(tempd)
        return set3

#     def separateInitAccDomains(self, space, domain, flatStructInfo, accIdxList):
#         tDomain = domain-domain
#         bsets = domain.get_basic_sets()
#         cs = []
#         for sd in flatStructInfo:
#             for sbs in sd.get_basic_sets():
#                 for c in sbs.get_constraints():
#                     goodc = True
#                     i=0
#                     while goodc and i < len(accIdxList):
#                         dimType, pos = space.get_var_dict()[accIdxList[i]]
#                         if c.is_equality():
#                             reva = c.get_aff().mul(Aff.read_from_str(c.get_ctx(),"{[]->[(-1)]}"))
#                             revc = Constraint.equality_from_aff(reva)
#                             goodc = c.involves_dims(dimType, pos, 1) and (c.is_lower_bound(dimType, pos) or revc.is_lower_bound(dimType, pos))
#                         else:
#                             goodc = c.involves_dims(dimType, pos, 1) and c.is_lower_bound(dimType, pos)
#                         i+=1
#                     if goodc:
#                         cs += [Constraint.equality_from_aff(c.get_aff())]
#         for c in cs:
#             for bs in bsets:
#                 tDomain = tDomain.union(bs.add_constraint(c))
#         initDomain = domain.intersect(tDomain)
#         return initDomain
    
    def computeInitDomain(self, space, initDomain, domain, flatStructInfo, accIdxList):
        tDomain = domain-domain
#         bsets = domain.get_basic_sets()
#         for sd in flatStructInfo:
#             for sbs in sd.get_basic_sets():
        for bs in domain.get_basic_sets():
            s_cpy = bs
            for idx in accIdxList:
                dimType, pos = space.get_var_dict()[idx]
                cs = []
                for c in bs.get_constraints():
                    if c.involves_dims(dimType, pos, 1) and c.is_lower_bound(dimType, pos) and not c.is_equality():
                        cs.append(c)
                if cs:
                    if len(cs) > 1:
                        aff_re = re.compile("{ \[.*\] -> \[(.*)\] }")
                        max_args = []
                        for c in cs:
                            saff = str(c.set_coefficient_val(dimType, pos, 0).get_aff().mul(Aff.read_from_str(domain.get_ctx(),"{[]->[(-1)]}")) )
                            arg = aff_re.search(saff).group(1)
                            max_args.append( arg )
                        smax = "max(" + max_args[0] + ", " + max_args[1] + ")"
                        for arg in max_args[2:]:
                            smax = "max(" + smax + ", " + arg + ")"
                        pwaff = PwAff.read_from_str(domain.get_ctx(), "{["+(",".join(self.indices))+"]->[("+idx+" - "+smax+")]}")
                        s = s_cpy - s_cpy
                        for pc in pwaff.get_pieces():
                            s = s.union( pc[0].add_constraint(Constraint.equality_from_aff(pc[1])) )
                        s_cpy = s.intersect(s_cpy)
                    else:
                        s_cpy = s_cpy.add_constraint(Constraint.equality_from_aff(cs[0].get_aff()))
            
            tDomain = tDomain.union(s_cpy)      
#         for bs in bsets:
#                 tDomain = tDomain.union(bs.add_constraints(cs))
        tInitDomain = tDomain.coalesce().remove_redundancies()
#         tInitDomain = domain.intersect(tDomain) # Is this necessary??
        if initDomain.is_empty():
            return tInitDomain
        #Compare intersection with previous initDomain projecting out the accIndices
        tPrjOut, iPrjOut = tInitDomain, initDomain
        tSpace = space
        for i in accIdxList:
            dimType, pos = tSpace.get_var_dict()[i]
            tPrjOut = tPrjOut.project_out(dimType, pos, 1)
            iPrjOut = iPrjOut.project_out(dimType, pos, 1)
            tSpace = tPrjOut.get_space()
        intPrjOut = tPrjOut.intersect(iPrjOut)
        if not intPrjOut.is_empty():
            initDomain = tInitDomain - tInitDomain.intersect(align_spaces(intPrjOut,domain))
        else:
#             initDomain = domain-domain
            initDomain = tInitDomain
        return initDomain

    def compute_full_init_domain(self, space, domain, accIdxList):
        tDomain = domain-domain
        aff_re = re.compile("{ \[.*\] -> \[(.*)\] }")

        for bs in domain.get_basic_sets():
            s_cpy = bs
            for idx in accIdxList:
                dimType, pos = space.get_var_dict()[idx]
                cs = []
                for c in bs.get_constraints():
                    if c.involves_dims(dimType, pos, 1) and c.is_lower_bound(dimType, pos) and not c.is_equality():
                        cs.append(c)
                if cs:
                    if len(cs) > 1:
                        max_args = []
                        for c in cs:
                            saff = str(c.set_coefficient_val(dimType, pos, 0).get_aff().mul(Aff.read_from_str(domain.get_ctx(),"{[]->[(-1)]}")) )
                            arg = aff_re.search(saff).group(1)
                            max_args.append( arg )
                        smax = "max(" + max_args[0] + ", " + max_args[1] + ")"
                        for arg in max_args[2:]:
                            smax = "max(" + smax + ", " + arg + ")"
                        pwaff = PwAff.read_from_str(domain.get_ctx(), "{["+(",".join(self.indices))+"]->[("+idx+" - "+smax+")]}")
                        s = s_cpy - s_cpy
                        for pc in pwaff.get_pieces():
                            s = s.union( pc[0].add_constraint(Constraint.equality_from_aff(pc[1])) )
                        s_cpy = s.intersect(s_cpy)
                    else:
                        s_cpy = s_cpy.add_constraint(Constraint.equality_from_aff(cs[0].get_aff()))
            
            tDomain = tDomain.union(s_cpy)      

        initDomain = tDomain.coalesce().remove_redundancies()
        
        #Now need to make sure we get ride of overlapping init areas across BSs (Following is meant for Set with 2 BSs)
        if len(initDomain.get_basic_sets()) > 1:
            dom_wo_acc = initDomain.universe_like()
            for idx in accIdxList:
                dimType, pos = dom_wo_acc.get_space().get_var_dict()[idx]
                dom_wo_acc = dom_wo_acc.remove_dims(dimType, pos, 1)
            
            dom_wo_acc = dom_wo_acc-dom_wo_acc
            union_projected_out_bss = None 

            for bs in initDomain.get_basic_sets():
                bs_wo_acc = bs
                for idx in accIdxList:
                    dimType, pos = bs_wo_acc.get_space().get_var_dict()[idx]
                    bs_wo_acc = bs_wo_acc.project_out(dimType, pos, 1)
                if union_projected_out_bss is None:
                    union_projected_out_bss = bs_wo_acc
                else:
                    intersection = union_projected_out_bss.intersect(bs_wo_acc)
                    union_projected_out_bss.union(bs_wo_acc)
                    if not intersection.is_empty():
                        dom_wo_acc = dom_wo_acc.union(intersection)
            
            overlapping_area = initDomain.intersect(align_spaces(dom_wo_acc, initDomain))
            
            # Remove the overlapping area that will be replaced with one of its faces 
            initDomain = initDomain - overlapping_area
            
            overlapping_area_only_acc = overlapping_area
            for idx in self.indices:
                if idx not in accIdxList:
                    dimType, pos = overlapping_area_only_acc.get_space().get_var_dict()[idx]
                    overlapping_area_only_acc = overlapping_area_only_acc.project_out(dimType, pos, 1)
            
            for idx in accIdxList:
                dimType, pos = overlapping_area_only_acc.get_space().get_var_dict()[idx]
                cs = []
                for bs in overlapping_area_only_acc.get_basic_sets(): 
                    for c in bs.get_constraints():
                        if c.involves_dims(dimType, pos, 1) and ( c.is_lower_bound(dimType, pos) or c.is_equality() ):
                            cs.append(c)
                if cs:
                    if len(cs) > 1:
                        min_args = []
                        for c in cs:
                            saff = str(c.set_coefficient_val(dimType, pos, 0).get_aff().mul(Aff.read_from_str(domain.get_ctx(),"{[]->[(-1)]}")) )
                            arg = aff_re.search(saff).group(1)
                            min_args.append( arg )
                        smin = "min(" + min_args[0] + ", " + min_args[1] + ")"
                        for arg in min_args[2:]:
                            smin = "min(" + smin + ", " + arg + ")"
                        pwaff = PwAff.read_from_str(domain.get_ctx(), "{["+(",".join(self.indices))+"]->[("+idx+" - "+smin+")]}")
                        s = overlapping_area - overlapping_area
                        for pc in pwaff.get_pieces():
                            s = s.union( pc[0].add_constraint(Constraint.equality_from_aff(pc[1])) )
                        overlapping_area = s.intersect(overlapping_area)
                    else:
                        aff_out = aff_re.search(str(cs[0].get_aff())).group(1)
                        aff = Aff.read_from_str(domain.get_ctx(), "{["+(",".join(self.indices))+"]->[("+aff_out+")]}")
                        overlapping_area = overlapping_area.add_constraint(Constraint.equality_from_aff(aff))
            
            initDomain = initDomain.union(overlapping_area)
        
        return initDomain
        
    def createOpenSCoP(self):
        text = "<OpenScop>\n\nSIGMA\n\n"
        #Context
        text += "CONTEXT\n0 2 0 0 0 0\n\n0\n\n" # 2 columns e/i | 1 + Parameters are not provided
        text += str(self.numStmts) + "\n\n"
        for s in self.stmts:
            text += s
        text += "<scatnames>\n"
        text += " ".join(self.scatnames)
        text += "\n</scatnames>\n\n"
        text += "</OpenScop>\n" # 2 columns e/i | 1 + Parameters are not provided
        f = open("/tmp/temp.scop", 'w')
        f.write(text)
        f.close()

    def addStmts(self, polyStmts):
        self.numStmts += len(polyStmts)
        for ps in polyStmts:
            text = ""
            text += "2\n\n" # Num. of relations describing the statement (now only domain+sched)
            text += "#----------------------------------------------------------------\n"
            text += "DOMAIN\n"
            f = open("/tmp/temp.scop", 'w')
            ps['domain'].print_(f, 0, format.EXT_POLYLIB)
            f.close()
            f = open("/tmp/temp.scop", 'r')
            sdom = f.read()
            f.close()
            text += sdom
            text += "SCATTERING\n"
            f = open("/tmp/temp.scop", 'w')
            ps['sched'].print_(f, 0, format.EXT_POLYLIB)
            f.close()
            f = open("/tmp/temp.scop", 'r')
            ssched = f.read()
            f.close()
            text += ssched
            text += "\n1\n" #Statement body is provided
            text += "\n<body>\n"
            idxList = ps['idxlist']
#             idxList = self.indices
            text += str(len(idxList)) + "\n"
            text += " ".join(idxList) + "\n"
            text += str(ps['stmt']) + "\n"
            text += str(ps['eq_id']) + "\n"
            text += ps['outinfo'][0] + "\n"
            if len(ps['outinfo']) > 1:
#                 text += "1\n"
                text += ps['outinfo'][1] + "\n"
            text += "\n</body>\n"
            text += "\n#----------------------------------------------------------------\n\n"
            self.stmts.append(text)

    def createSigmaSource(self):
#         import example_cloog
        import sigmacloog
        s = sigmacloog.tosigma_str("/tmp/temp.scop")
        self.sigmaSource += str(s)

#     def computeScheds(self, root):
#         for ps in root.getPolyStmts():
#             ps['sched'] = self.computeSched(ps)

    def computeScheds(self, expr, prefix=None):
        prefix = [] if prefix is None else prefix
        if isinstance(expr, llBlock):
            i = 0
            for s in expr:
                new_prefix = prefix + [ str(i) ]
                i += 1
                self.computeScheds(s, new_prefix)
        elif isinstance(expr, llFor):
            new_prefix = prefix + [ str(expr.idx) ]
            self.computeScheds(expr.body, new_prefix)
        elif isinstance(expr, llStmt):
            new_prefix = prefix + ['0']*(self.scat_counter-len(prefix)+1)
            for ps in expr.eq.getPolyStmts():
                ps['sched'] = self.computeSched(ps, self.opts['stmts_ids'][expr], new_prefix)
        elif isinstance(expr, llIf):
            for b in expr.bodys:
                self.computeScheds(b, prefix)


    def computeSched(self, polyStmt, ids_order, prefix):
        varDict = polyStmt['domain'].get_space().get_var_dict()
        schedList = list(prefix)
        for i in ids_order:
            if not i in varDict:
                schedList.append('0')
            else:
                schedList.append(i)
##         schedList.append(str(polyStmt['oporder']))
#         schedList.extend( ['0']*(len(self.scatnames)-len(schedList)) )
        varList = sorted(varDict.items(), key=lambda entry: entry[1][1])
        idxList = [ e[0] for e in varList ] 
        polyStmt['idxlist'] = idxList
##         m = Map("{ ["+",".join(self.indices)+"] -> ["+",".join(schedList)+"] }")
        m = Map("{ ["+",".join(idxList)+"] -> ["+",".join(schedList)+"] }")
        return m
    
    def reorderIdxList(self, idxList, iPriority, opts):
        order = opts['indexorder']
        for idx in iPriority:
            p = iPriority[idx]
            t = ( p[order[0]], p[order[1]], p[order[2]] )
            iPriority[idx] = t
        ordPrioList = sorted(iPriority.items(), key=lambda idxp: idxp[1])
        ordSym = [ idxp[0] for idxp in ordPrioList ]
        ordIdxList = [None]*len(idxList)
        for idx in idxList:
            ordIdxList[ordSym.index(idx)] = idx
        return ordIdxList

    def correctDomains(self, polyStmts):
        for ps in polyStmts:
            ps['domain'] = self.correctDomain(ps['domain'])
            ps['eq_id'] = self.eq_id

    def correctDomain(self, domain_list, indices=None):
        indices = self.indices if indices is None else indices
        res = []
        for tDomain in domain_list: 
            for i in self.indices:
                vardict = tDomain.get_space().get_var_dict()
                if i in vardict and not tDomain.involves_dims(vardict[i][0], vardict[i][1], 1):
                    tDomain = tDomain.project_out(vardict[i][0], vardict[i][1], 1)
            res.append(tDomain)
        del domain_list
        return res
                
    def fuseStmtWithSub(self, domain, subexpr, mReduceDims, oAccMap, includeAccPss=False, pos=None, extra_ids=None):
        pss = []
        if subexpr is not None:
#             tdReduced = mReduceDims.intersect_domain(domain).range()
#             tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
            for ps in subexpr.getPolyStmts():
                if includeAccPss or not ps['acc']:
#                     if extra_ids is not None and (extra_ids[0] or extra_ids[1]):
#                         if pos == 0: # To make it intersectable you extend one operand's touched with extra ids of the other
#                             ps_touched = ps['touched'].add_dims(dim_type.set, len(extra_ids[1]))
#                         else:
#                             ps_touched = ps['touched'].insert_dims(dim_type.set, 2, len(extra_ids[0]))
#                     else:
#                         ps_touched = ps['touched']
#                     touch_int = tdTransformedByOAcc.intersect(ps_touched)
#                     if touch_int.is_empty():
#                         continue
                    # The code above was probably introduced to handle same domains (like from 
                    # different matrix partitions) touch different areas of a matrix. I think there was one
                    # major flaw: using the reduceDims map from current expression can be meaningless.
                    tdReduced = ps['reducedims'].intersect_domain(domain).range()
                    for d,s in zip(ps['domain'], ps['stmt']):
                        psTdReduced = ps['reducedims'].intersect_domain(d).range()
                        if not tdReduced.intersect(psTdReduced).is_empty():
                            psDomInt = domain.intersect(d)
                            if not psDomInt.is_empty():
                                pss.append((psDomInt,s,ps['acc']))
        return pss
    
    def genGSSeq(self, imfList, acc=False, accSign=None):
        accSign = '' if not accSign else accSign
        accPrefix = ("$" + accSign) if acc else "" 
        p = accPrefix + "[" + str(imfList[0][0]) + "," + str(imfList[0][1]) + "]"
        for i in imfList[1:]:
            p += accPrefix + "[" + str(i[0]) + "," + str(i[1]) + "]"
#         if len(imfList)>1:
#             p += ("$" if acc else "") + "[" + str(imfList[-1][0]) + "," + str(imfList[-1][1]) + "]"
        return p
    
    def getNonTileMatrix(self, expr):
        if isinstance(expr, Quantity) or isinstance(expr, Tile):
            return expr.getNonTileOut()
        return None
    
    def getUnusedIds(self, imfList):
        usedIds = []
        for imf in imfList:
            usedIds.extend(imf.getAtoms())
        unusedIdx = [ idx for idx in self.indices if idx not in usedIds ]
        return unusedIdx

    def buildUnStmtLists(self, expr, mat, op, domain, pi, access, oAccSet, mReduceDims, oAccMap, includeAccPss=None, par=None, pos=None, acc_ids=None):
        includeAccPss = False if includeAccPss is None else includeAccPss
        par = False if par is None else par

        def _buildRet(td, inp, domList, inList, opList):
            inp = (StmtExpr([ inp ], wrap=['(',')']) if par else inp) if access[3] is None else StmtExpr([inp], access[3])                                                               
            domList.append(td)
            inList.append([inp])
            opList.append(op)
#             oTargetAccess = [ a for a in oAccess if not self.joinAlignedSets(oAccess[a], td, self.globalspace).is_empty() ]
#             oTargetList.append(oTargetAccess)
        
        tDomainList, inputsList, opList = [], [], []
        accDomainList, accInputsList, accOpList = [], [], []
        tDomain = self.joinAlignedSets(pi['access'][access], oAccSet, self.globalspace)
        tDomain = self.joinAlignedSets(tDomain, domain, self.globalspace)
#         mat = expr.getNonTileOut()
        
        if mat is None:
            pss = self.fuseStmtWithSub(tDomain, expr, mReduceDims, oAccMap, includeAccPss=includeAccPss, pos=pos, extra_ids=acc_ids)
            if pss:
                for ps in pss:
                    td = ps[0]
                    inp = ps[1].removeWrap()
#                     inp = ps[1]['stmt'].removeWrap()
#                     if ps[1]['acc']: 
                    if ps[2]: 
                        _buildRet(td, inp, accDomainList, accInputsList, accOpList)
                    else:
                        _buildRet(td, inp, tDomainList, inputsList, opList)
        else:
#             inp = StmtExpr([mat.name+self.genGSSeq(access[1])])            
            inp = StmtExpr([mat.toLL()+self.genGSSeq(access[1])])            
            _buildRet(tDomain, inp, tDomainList, inputsList, opList)

        return (tDomainList, accDomainList, inputsList, accInputsList, opList, accOpList)
        
    def buildBinStmtLists(self, exprs, mats, op, domain, lpi, rpi, access, oAccSet, mReduceDims, oAccMap, includeAccPss=None, par=None, acc_ids=None):
        includeAccPss = (False, )*2 if includeAccPss is None else includeAccPss
        par = (False, )*2 if par is None else par
        
        def _buildRet(td, lin, rin, domList, inList, opList):
            lin = (StmtExpr([ lin ], wrap=['(',')']) if par[0] else lin) if access[0][3] is None else StmtExpr([lin], access[0][3])                                                               
            rin = (StmtExpr([ rin ], wrap=['(',')']) if par[1] else rin) if access[1][3] is None else StmtExpr([rin], access[1][3])                                                               
            inputs = [lin, rin]
            domList.append(td)
            inList.append(inputs)
            opList.append(op)

        tDomainList, inputsList, opList = [], [], []
        accDomainList, accInputsList, accOpList = [], [], []
        tDomain = self.joinAlignedSets(lpi['access'][access[0]], rpi['access'][access[1]], self.globalspace)
        tDomain = self.joinAlignedSets(tDomain, oAccSet, self.globalspace)
        tDomain = self.joinAlignedSets(tDomain, domain, self.globalspace)

        if mats[0] is None:
            pssl = self.fuseStmtWithSub(tDomain, exprs[0], mReduceDims, oAccMap, includeAccPss=includeAccPss[0], pos=0, extra_ids=acc_ids)
            if pssl:
                for psl in pssl:
                    td = psl[0]
                    lin = psl[1].removeWrap()
                    if mats[1] is None:
                        pssr = self.fuseStmtWithSub(td, exprs[1], mReduceDims, oAccMap, includeAccPss=includeAccPss[1], pos=1, extra_ids=acc_ids)
                        if pssr:
                            for psr in pssr:
                                td = psr[0]
                                rin = psr[1].removeWrap()
                                if psl[2] or psr[2]: 
                                    _buildRet(td, lin, rin, accDomainList, accInputsList, accOpList)
                                else:
                                    _buildRet(td, lin, rin, tDomainList, inputsList, opList)
                    else:
                        rin = StmtExpr([mats[1].toLL()+self.genGSSeq(access[1][1])])            
                        if psl[2]: 
                            _buildRet(td, lin, rin, accDomainList, accInputsList, accOpList)
                        else:
                            _buildRet(td, lin, rin, tDomainList, inputsList, opList)
        else:
            lin = StmtExpr([mats[0].toLL()+self.genGSSeq(access[0][1])])
            if mats[1] is None:            
                pssr = self.fuseStmtWithSub(tDomain, exprs[1], mReduceDims, oAccMap, includeAccPss=includeAccPss[1], pos=1, extra_ids=acc_ids)
                if pssr:
                    for psr in pssr:
                        td = psr[0]
                        rin = psr[1].removeWrap()
                        if psr[2]: 
                            _buildRet(td, lin, rin, accDomainList, accInputsList, accOpList)
                        else:
                            _buildRet(td, lin, rin, tDomainList, inputsList, opList)
            else:
                rin = StmtExpr([mats[1].toLL()+self.genGSSeq(access[1][1])])            
                _buildRet(tDomain, lin, rin, tDomainList, inputsList, opList)
        return (tDomainList, accDomainList, inputsList, accInputsList, opList, accOpList)
    
    def set_from_ctx(self, ctx):
        for_ctx = filter(lambda c: isinstance(c, llFor), ctx)
        if_ctx = filter(lambda c: isinstance(c, llIf), ctx)
        constr_list = [ "(exists s: " + str(c.idx) + "="+str(c.s)+"s and " + str(c.lb) + " <= " + str(c.idx) + " <= " + str(c.ub) + ")" for c in for_ctx ]
        constr_list.extend( [c.conds[0].getIslStr() for c in if_ctx] )
        sCst = " and ".join(constr_list)
        sIndices = ",".join(self.indices)
        return Set("{["+sIndices+"] : "+sCst+"}")
        
    def get_out_acc_set_and_map(self, expr, blk_out, ctx):
        trailIds = [str(idx) for idx in expr.accIds]
        trailIds.extend( [str(c.idx) for c in ctx if isinstance(c, llFor)] )
        sTrailIds = ""
        if expr.accIds or ctx:
            sTrailIds = "," + ",".join(trailIds)
        fullOAccSet = Set("{[i,j" + sTrailIds + "]: 1=0}")
        oAccMap = blk_out.getFlatAccessMapND(trail=trailIds)
        return (sTrailIds, fullOAccSet, oAccMap)
        
    def llProgram(self, llprog):
        getattr(self, llprog.stmtList.__class__.__name__)(llprog.stmtList, [])
    
    def llBlock(self, blk, ctx):
        for b in blk:
            getattr(self, b.__class__.__name__)(b, ctx)

    def llFor(self, llfor, ctx):
        getattr(self, llfor.body.__class__.__name__)(llfor.body, ctx+[ llfor ] )

    def llIf(self, llif, ctx):
        getattr(self, llif.bodys[0].__class__.__name__)(llif.bodys[0], ctx+[ llif ] )

    def llStmt(self, llstmt, ctx):
        baselevel = self.baselevel
        if not llstmt.can_gen_with_nublac(self.nublac):
            self.baselevel = 2
        #print "Entering llStmt..."
        getattr(self, llstmt.eq.__class__.__name__)(llstmt.eq, ctx )
        self.baselevel = baselevel
        self.correctDomains(llstmt.eq.getPolyStmts())
        self.eq_id += 1

    def Assign(self, expr, ctx):
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], ctx)
        
        if isinstance(expr.inexpr[1], Tile):
            blkRhs = expr.getInexprMat(1)
            blkOut = self.subsWithOut.get((self.eq_id, expr.inexpr[1]), expr.inexpr[1]).getOut() 
#             blkOut = expr.getOut() 

            set_ctx = self.set_from_ctx(ctx)
            
            rMat = self.getNonTileMatrix(expr.inexpr[1])
            oMat = self.subsWithOut.get((self.eq_id, expr.inexpr[1]), expr.inexpr[1]).getNonTileOut()

            rPInfo = blkRhs.getPolyInfo(self.indices, baselevel=self.baselevel)
            oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)

            expr.accIds = []
            sTrailIds, fullOAccSet, oAccMap = self.get_out_acc_set_and_map(expr, blkOut, ctx)
            
            polyStmts = []
            for r in range(len(rPInfo)):
                for c in range(len(rPInfo[0])):
                    rpi,opi = rPInfo[r][c], oPInfo[r][c]
    
                    cpyAccess = [(rAccess,oAccess) for rAccess in rpi['access'] for oAccess in opi['access']]
                    cpyStruct = [(rStr,oStr) for rStr in rpi['struct'].items() for oStr in opi['struct'].items() if not issubclass(oStr[0], ConstantMatrix) ]
                    for cStr in cpyStruct:
                        cpyDomain = self.joinAlignedSets(cStr[0][1], cStr[1][1], self.globalspace)
                        cpyDomain = self.joinAlignedSets(cpyDomain, rpi['tiling'], self.globalspace)
                        cpyDomain = self.joinAlignedSets(cpyDomain, set_ctx, self.globalspace)
                        if cpyDomain.is_empty():
                            continue
                        for cAccess in cpyAccess:
                            oAccess = cAccess[1]
                            oAccSet = opi['access'][oAccess] 
                            mReduceDims = Map("{["+(",".join(self.indices))+"]->[i,j"+sTrailIds+"]: " + str(oAccess[2][0].of(0)) + "=i and " + str(oAccess[2][1].of(0)) + "=j}")
                            tDomainList, inputsList, opList = [], [], []
                            tDomainList, _, inputsList, _, opList, _ = \
                            self.buildUnStmtLists(expr.inexpr[1], rMat, None, cpyDomain, rpi, cAccess[0], oAccSet, mReduceDims, oAccMap)
                            if tDomainList:
                                for td,inputs,op in zip(tDomainList,inputsList,opList):
                                    if not td.is_empty():
                                        tdReduced = mReduceDims.intersect_domain(td).range()
                                        tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
#                                         if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
#                                             fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
#                                             polyStmt = {}
                                        overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                        polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                        if new_ps:
                                            polyStmt['touched'] = tdTransformedByOAcc
                                            polyStmt['stmt'] = []
                                            polyStmt['perm_oacc'] = []
                                            polyStmt['domain'] = []
                                            polyStmt['outinfo'] = []
                                        scat = self.genGSSeq(oAccess[1])
                                        oMat2ll = oMat.toLL(sep=True) 
                                        if len(oMat2ll) > 1:
                                            wrap = [oMat2ll[1]+scat, ""]
                                        else:
                                            wrap = [scat, ""]
                                        finStmt = StmtExpr(inputs, op)
                                        finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                        polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                        polyStmt['perm_oacc'].append( oAccess[3] )
                                        polyStmt['domain'].append( td )
                                        polyStmt['acc'] = False
                                        polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                        if new_ps:
                                            polyStmts.append(polyStmt)
    
            expr.setPolyStmts(polyStmts)
        else:
            expr.setPolyStmts(expr.inexpr[1].getPolyStmts())
        
    def Mul(self, expr, ctx):
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], ctx)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], ctx)
#         opOrder = self.opOrder
#         self.opOrder+=1
        
        blkLhs = expr.getInexprMat(0)
        blkRhs = expr.getInexprMat(1)
        blkOut = self.subsWithOut.get((self.eq_id, expr), expr).getOut() 
#         blkOut = expr.getOut() 
        
        set_ctx = self.set_from_ctx(ctx)
        
        lMat, rMat = self.getNonTileMatrix(expr.inexpr[0]), self.getNonTileMatrix(expr.inexpr[1])
        oMat = self.subsWithOut.get((self.eq_id, expr), expr).getNonTileOut()
        
        expr.accIds = [ i for i in self.indices if i in blkLhs.idxPosAndLevInfo and blkLhs.idxPosAndLevInfo[i][2] == 1 ]

        lPinfo = blkLhs.getPolyInfo(self.indices, baselevel=self.baselevel)
        rPInfo = blkRhs.getPolyInfo(self.indices, baselevel=self.baselevel)
        oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)

        sTrailIds, fullOAccSet, oAccMap = self.get_out_acc_set_and_map(expr, blkOut, ctx)

        fullDomain = self.getEmptyDomain()
        for r in range(len(lPinfo)):
            for c in range(len(rPInfo[0])):
                for kc in range(len(lPinfo[0])):
                    lpi,rpi = lPinfo[r][kc], rPInfo[kc][c]
                    prodStruct = [(lStr,rStr) for lStr in lpi['struct'].items() if lStr[0] is not ZeroMatrix for rStr in rpi['struct'].items() if rStr[0] is not ZeroMatrix ]
                    for pStr in prodStruct:
                        lTSDomain = self.joinAlignedSets(pStr[0][1], lpi['tiling'], self.globalspace)
                        rTSDomain = self.joinAlignedSets(pStr[1][1], rpi['tiling'], self.globalspace)
                        mulDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)
                        mulDomain = self.joinAlignedSets(mulDomain, set_ctx, self.globalspace)
                        fullDomain = fullDomain.union(mulDomain).coalesce().remove_redundancies()
        initDomain = self.compute_full_init_domain(self.globalspace, fullDomain, expr.accIds)
        
        polyStmts = []
        for r in range(len(lPinfo)):
            for c in range(len(rPInfo[0])):
                for kc in range(len(lPinfo[0])):
                    lpi,rpi,opi = lPinfo[r][kc], rPInfo[kc][c], oPInfo[r][c]
                    prodAccess = [(lAccess,rAccess, oAccess) for lAccess in lpi['access'] for rAccess in rpi['access'] for oAccess in opi['access']]
                    prodStruct = [(lStr,rStr, oStr) for lStr in lpi['struct'].items() if lStr[0] is not ZeroMatrix for rStr in rpi['struct'].items() if rStr[0] is not ZeroMatrix \
                                  for oStr in opi['struct'].items() if not issubclass(oStr[0], ConstantMatrix)]
                    for pStr in prodStruct:
                        lTSDomain = self.joinAlignedSets(pStr[0][1], lpi['tiling'], self.globalspace)
                        rTSDomain = self.joinAlignedSets(pStr[1][1], rpi['tiling'], self.globalspace)
                        mulDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)
                        mulDomain = self.joinAlignedSets(mulDomain, pStr[2][1], self.globalspace)
                        mulDomain = self.joinAlignedSets(mulDomain, set_ctx, self.globalspace)
                        locInitDomain = initDomain.intersect(mulDomain)
                        accDomain = mulDomain - locInitDomain

                        for pAccess in prodAccess:
                            oAccess = pAccess[2]
                            oAccSet = opi['access'][oAccess] 
                            mReduceDims = Map("{["+(",".join(self.indices))+"]->[i,j"+sTrailIds+"]: " + str(oAccess[2][0].of(0)) + "=i and " + str(oAccess[2][1].of(0)) + "=j}")
                            if not locInitDomain.is_empty():
                                tDomainList, opList, inputsList = [], [], []
                                tDomainList, _, inputsList, _, opList, _ = \
                                self.buildBinStmtLists(expr.inexpr, (lMat, rMat), Mul, locInitDomain, lpi, rpi, pAccess, oAccSet, mReduceDims, oAccMap, par=(True,True), acc_ids=[expr.accIds,expr.accIds])
                                if tDomainList:
                                    for td, inputs, op in zip(tDomainList, inputsList, opList):
                                        if not td.is_empty():
                                            tdReduced = mReduceDims.intersect_domain(td).range()
                                            tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
#                                             if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
#                                                 fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
#                                                 polyStmt = {}
                                            overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                            polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                            if new_ps:
                                                polyStmt['touched'] = tdTransformedByOAcc
                                                polyStmt['reducedims'] = mReduceDims 
                                                polyStmt['stmt'] = []
                                                polyStmt['perm_oacc'] = []
                                                polyStmt['domain'] = []
                                                polyStmt['outinfo'] = []
                                            scat = self.genGSSeq(oAccess[1])
                                            oMat2ll = oMat.toLL(sep=True) 
                                            if len(oMat2ll) > 1:
                                                wrap = [oMat2ll[1]+scat, ""]
                                            else:
                                                wrap = [scat, ""]
                                            finStmt = StmtExpr(inputs, op)
                                            finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                            polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                            polyStmt['perm_oacc'].append( oAccess[3] )
                                            polyStmt['domain'].append( td )
                                            polyStmt['acc'] = False
                                            polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                            if new_ps:
                                                polyStmts.append(polyStmt)
                            
                            if not accDomain.is_empty():
                                tDomainList, opList, inputsList = [], [], []
                                tDomainList, _, inputsList, _, opList, _ = \
                                self.buildBinStmtLists(expr.inexpr, (lMat, rMat), Mul, accDomain, lpi, rpi, pAccess, oAccSet, mReduceDims, oAccMap, par=(True,True), acc_ids=[expr.accIds,expr.accIds])
                                if tDomainList:
                                    for td, inputs, op in zip(tDomainList, inputsList, opList):
                                        if not td.is_empty():
                                            tdReduced = mReduceDims.intersect_domain(td).range()
                                            tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
#                                             if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
#                                                 fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
#                                                 polyStmt = {}
                                            overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                            polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                            if new_ps:
                                                polyStmt['touched'] = tdTransformedByOAcc
                                                polyStmt['reducedims'] = mReduceDims 
                                                polyStmt['stmt'] = []
                                                polyStmt['perm_oacc'] = []
                                                polyStmt['domain'] = []
                                                polyStmt['outinfo'] = []
                                            scat = self.genGSSeq(oAccess[1])
                                            oMat2ll = oMat.toLL(acc=True, sep=True) 
                                            if len(oMat2ll) > 1:
                                                wrap = ["$"+oMat2ll[1]+self.genGSSeq(oAccess[1], acc=True), ""]
                                            else:
                                                wrap = [self.genGSSeq(oAccess[1], acc=True),""]
                                            finStmt = StmtExpr(inputs, op)
                                            finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                            polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                            polyStmt['perm_oacc'].append( oAccess[3] )
                                            polyStmt['domain'].append( td )
                                            polyStmt['acc'] = True
                                            polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                            if new_ps:
                                                polyStmts.append(polyStmt)
        
        expr.setPolyStmts(polyStmts)

    def LDiv(self, expr, ctx):
        blkLhs = expr.getInexprMat(0)
        if isinstance(blkLhs, LowerTriangular):
            self.forward_sub(expr, ctx)
        elif isinstance(blkLhs, UpperTriangular):
            self.backward_sub(expr, ctx)
            
#         self.LDiv2(expr, opts)

    def forward_sub(self, expr, ctx):
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], ctx)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], ctx)
#         opOrder = self.opOrder
#         self.opOrder+=1
        
        blkLhs = expr.getInexprMat(0)
        blkRhs = expr.getInexprMat(1)
        blkOut = expr.getOut() 

        set_ctx = self.set_from_ctx(ctx)

        expr.accIds = expr.inexpr[0].accIds + expr.inexpr[1].accIds
        sTrailIds, fullOAccSet, oAccMap = self.get_out_acc_set_and_map(expr, blkOut, ctx)

        polyStmts = []
        
#         lMat, rMat = self.getNonTileMatrix(expr.inexpr[0]), self.getNonTileMatrix(self.subsWithOut.get(expr, expr))
#         
#         lPinfo = blkLhs.getPolyInfo(self.indices, baselevel=self.baselevel, extrainfo=['StrictLower', 'Diag', 'TopLeft'])
#         rPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)
# 
#         accIdx = [ i for i in self.indices if i in blkLhs.idxPosAndLevInfo and blkLhs.idxPosAndLevInfo[i][2] == 1 ]
#         
#         polyStmts = []
# 
#         TList = [[],[]]
#         for r in range(len(lPinfo)):
#             for c in range(len(rPInfo[0])):
#                 
# #                 Temp = Matrix("P"+str(globalSSAIndex()), rPInfo[r][c]['topblk'], (1,1))
#                 Temp = Matrix("P"+str(globalSSAIndex()), rPInfo[r][c]['topblk'], tuple(blkOut.getPartitionSize(r,c)) )
#                 self.mDict[Temp.name] = Matrix(Temp.name, scalar_block(), Temp.getFlatSize(), attr={ 'o':True, 'i':True, 't':True })
#                 Temp.spaceIdxNames = [ deepcopy(s) for s in blkRhs.spaceIdxNames ]
#                 for d in range(2):
#                     if(Temp.size[d] == 1):
#                         Temp.spaceIdxNames[d][0] = '0'
# #                 Temp.spaceIdxNames[0][0] = '0'
# #                 Temp.spaceIdxNames[1][0] = '0'
#                 tPInfo = Temp.getPolyInfo(self.indices, baselevel=self.baselevel)
#                 TList[r].append((Temp, tPInfo))
#                 
#                 initDomain = self.getEmptyDomain()
# 
#                 for kc in range(len(lPinfo[0])):
#                     lpi,rpi = lPinfo[r][kc], rPInfo[kc][c]
# 
# #                     oAccess = tPInfo[0][0]['access']
#                     prodAccess = [(lAccess,rAccess,oAccess) for lAccess in lpi['access'] for rAccess in rpi['access'] for oAccess in tPInfo[0][0]['access']]
#                     prodStruct = [(lStr,rStr) for lStr in lpi['StrictLower'].items() if lStr[0] is Matrix for rStr in rpi['struct'].items() if rStr[0] is Matrix ]
#                     for pStr in prodStruct:
#                         lTSDomain = self.joinAlignedSets(pStr[0][1], lpi['tiling'], self.globalspace)
#                         rTSDomain = self.joinAlignedSets(pStr[1][1], rpi['tiling'], self.globalspace)
#                         mulDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)
# #                         locInitDomain = self.computeInitDomain(self.globalspace, initDomain, mulDomain, [lpi['flatstruct'], rpi['flatstruct']], accIdx)
#                         locInitDomain = self.computeInitDomain(self.globalspace, initDomain, mulDomain, [lTSDomain.convex_hull(), rTSDomain.convex_hull()], accIdx)
#                         accDomain = mulDomain - locInitDomain
#                         initDomain = initDomain.union(locInitDomain).coalesce().remove_redundancies()
# 
#                         for pAccess in prodAccess:
# #                             tDomain = self.joinAlignedSets(lpi['access'][pAccess[0]], rpi['access'][pAccess[1]], self.globalspace)
# #                             tDomain = self.joinAlignedSets(tDomain, mulDomain, self.globalspace)
# #                             if not tDomain.is_empty():
# #                                 #Determine Init instances
# #                                 locInitDomain = self.computeInitDomain(self.globalspace, initDomain, tDomain, [lpi['flatstruct'], rpi['flatstruct']], accIdx)
# #                                 accDomain = tDomain - locInitDomain
# #                                 initDomain = initDomain.union(locInitDomain).coalesce().remove_redundancies()
#                             oAccess = pAccess[2]
#                             oAccSet = tPInfo[0][0]['access'][oAccess] 
#                             if not locInitDomain.is_empty():                                    
# #                                     pssl = self.fuseStmtWithSub(locInitDomain, expr.inexpr[0])
# #                                     if pssl:
# #                                         locInitDomain = pssl[0][0]
# #                                         lin = pssl[0][1]['stmt'].removeWrap()
# #                                     else:
# #                                         lin = StmtExpr([lMat.name+self.genGSSeq(pAccess[0][1])])
# # #                                     pssr = self.fuseStmtWithSub(locInitDomain, expr.inexpr[1])
# # #                                     if pssr:
# # #                                         locInitDomain = pssr[0][0]
# # #                                         rin = pssr[0][1]['stmt'].removeWrap()
# # #                                     else:
# #                                     rin = StmtExpr([rMat.name+self.genGSSeq(pAccess[1][1])])
# #                                      
# #                                     lin = StmtExpr([ lin ], wrap=['(',')']) if pAccess[0][3] is None else StmtExpr([lin], pAccess[0][3])                                                               
# #                                     rin = StmtExpr([ rin ], wrap=['(',')']) if pAccess[1][3] is None else StmtExpr([rin], pAccess[1][3])                                                               
# #                                     inputs = [lin, rin]
#                                 tDomainList, opList, inputsList = [], [], []
#                                 tDomainList, _, inputsList, _, opList, _ = \
#                                 self.buildBinStmtLists((expr.inexpr[0],None), (lMat, rMat), Mul, locInitDomain, lpi, rpi, pAccess, oAccSet, par=(True,True))
#                                 if tDomainList:
#                                     for td, inputs, op in zip(tDomainList, inputsList, opList):
#                                         if not td.is_empty():
# #                                                 scat = self.genGSSeq(oAccess[0][1])
#                                             scat = self.genGSSeq(oAccess[1])
#                                             wrap = [scat,""]
#                                             polyStmt = {}
# #                                                 polyStmt['stmt'] = StmtExpr(inputs, op, wrap)
#                                             finStmt = StmtExpr(inputs, op)
#                                             finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
#                                             polyStmt['stmt'] = StmtExpr([finStmt], None, wrap)
#                                             polyStmt['outinfo'] = [Temp.name, scat]
# #                                                 polyStmt['domain'] = locInitDomain.coalesce().remove_redundancies()
#                                             polyStmt['domain'] = td
#                                             polyStmt['acc'] = False
#                                             polyStmt['oporder'] = opOrder
#                                             polyStmts.append(polyStmt)
#                             if not accDomain.is_empty():
# #                                     pssl = self.fuseStmtWithSub(accDomain, expr.inexpr[0])
# #                                     if pssl:
# #                                         accDomain = pssl[0][0]
# #                                         lin = pssl[0][1]['stmt'].removeWrap()
# #                                     else:
# #                                         lin = StmtExpr([lMat.name+self.genGSSeq(pAccess[0][1])])
# #                                     rin = StmtExpr([rMat.name+self.genGSSeq(pAccess[1][1])])
# #                                     lin = StmtExpr([ lin ], wrap=['(',')']) if pAccess[0][3] is None else StmtExpr([lin], pAccess[0][3])                                                               
# #                                     rin = StmtExpr([ rin ], wrap=['(',')']) if pAccess[1][3] is None else StmtExpr([rin], pAccess[1][3])                                                               
# #                                     inputs = [lin, rin]
#                                 tDomainList, opList, inputsList = [], [], []
#                                 tDomainList, _, inputsList, _, opList, _ = \
#                                 self.buildBinStmtLists((expr.inexpr[0],None), (lMat, rMat), Mul, accDomain, lpi, rpi, pAccess, oAccSet, par=(True,True))
#                                 if tDomainList:
#                                     for td, inputs, op in zip(tDomainList, inputsList, opList):
#                                         if not td.is_empty():
# #                                                 wrap = [self.genGSSeq(oAccess[0][1], acc=True),""]
#                                             wrap = [self.genGSSeq(oAccess[1], acc=True),""]
#                                             polyStmt = {}
#                                             polyStmt['stmt'] = StmtExpr(inputs, op, wrap)
#                                             polyStmt['outinfo'] = [Temp.name, self.genGSSeq(oAccess[1])]
# #                                                 polyStmt['domain'] = accDomain.coalesce().remove_redundancies()
#                                             polyStmt['domain'] = td
#                                             polyStmt['acc'] = True
#                                             polyStmt['oporder'] = opOrder
#                                             polyStmts.append(polyStmt)

        lPinfo = blkLhs.getPolyInfo(self.indices, baselevel=self.baselevel, extrainfo=['StrictLower', 'Diag', 'TopLeft'])
#         lPinfo = blkLhs.getPolyInfo(self.indices, baselevel=self.baselevel)
        rPInfo = blkRhs.getPolyInfo(self.indices, baselevel=self.baselevel)
        oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)
        lMat, rMat, oMat = self.getNonTileMatrix(expr.inexpr[0]), self.getNonTileMatrix(expr.inexpr[1]), self.subsWithOut.get((self.eq_id, expr), expr).getNonTileOut()
        
#         for r in range(len(lPinfo)):
#             for c in range(len(rPInfo[0])):
#                 Temp, tPInfo = TList[r][c]
#                 opi = oPInfo[r][c]
#                 for kc in range(len(lPinfo[0])):
#                     lpi,rpi = lPinfo[r][kc], rPInfo[kc][c]
# #                     oAccess = opi['access'].items()[0]
# #                     oAccess = opi['access']
#                     tAccess = tPInfo[0][0]['access'].items()[0]
#                     ldivAccess = [(lAccess,rAccess,oAccess) for lAccess in lpi['access'] for rAccess in rpi['access'] for oAccess in opi['access']]
#                     ldivStruct = [(lStr,rStr) for lStr in lpi['Diag'].items() for rStr in rpi['struct'].items() if rStr[0] is not ZeroMatrix ]
#                     tl = self.getEmptyDomain() if not lpi['TopLeft'] else lpi['TopLeft'].items()[0][1]
#                     for ldStr in ldivStruct:
#                         lTSDomain = self.joinAlignedSets(ldStr[0][1]-tl, lpi['tiling'], self.globalspace)
#                         rTSDomain = self.joinAlignedSets(ldStr[1][1], rpi['tiling'], self.globalspace)
#                         ldivDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)
# 
#                         for ldAccess in ldivAccess:
# #                             tDomain = self.joinAlignedSets(lpi['access'][ldAccess[0]], rpi['access'][ldAccess[1]], self.globalspace)
# #                             tDomain = self.joinAlignedSets(tDomain, ldivDomain, self.globalspace)
# #                             if not tDomain.is_empty():
# #                                 polyStmt = {}
# #                                 pssl = self.fuseStmtWithSub(tDomain, expr.inexpr[0])
# #                                 if pssl:
# #                                     tDomain = pssl[0][0]
# #                                     lin = pssl[0][1]['stmt'].removeWrap()
# #                                 else:
# #                                     lin = StmtExpr([lMat.name+self.genGSSeq(ldAccess[0][1])])
# #                                 pssr = self.fuseStmtWithSub(tDomain, expr.inexpr[1])
# #                                 if pssr:
# #                                     tDomain = pssr[0][0]
# #                                     rin = pssr[0][1]['stmt'].removeWrap()
# #                                 else:
# #                                     rin = StmtExpr([rMat.name+self.genGSSeq(ldAccess[1][1])])
# #                                 lin = StmtExpr([ lin ], wrap=['(',')']) if ldAccess[0][3] is None else StmtExpr([lin], ldAccess[0][3])                                                               
# #                                 rin = StmtExpr([ rin ], wrap=['(',')']) if ldAccess[1][3] is None else StmtExpr([rin], ldAccess[1][3])
# #                                 rin = StmtExpr([rin,StmtExpr([Temp.name+self.genGSSeq(tAccess[0][1])])], Sub, ["(",")"])                                          
# #                                 inputs = [lin, rin]
#                             oAccess = ldAccess[2]
#                             oAccSet = opi['access'][oAccess] 
#                             tDomainList, opList, inputsList = [], [], []
#                             tDomainList, _, inputsList, _, opList, _ = \
#                             self.buildBinStmtLists(expr.inexpr, (lMat, rMat), LDiv, ldivDomain, lpi, rpi, ldAccess, oAccSet, par=(True,True))
#                             if tDomainList:
#                                 for td, inputs, op in zip(tDomainList, inputsList, opList):
#                                     if not td.is_empty():
#                                         inputs[1] = StmtExpr([inputs[1],StmtExpr([Temp.name+self.genGSSeq(tAccess[0][1])])], Sub, ["(",")"]) 
# #                                         scat = self.genGSSeq(oAccess[0][1])
#                                         scat = self.genGSSeq(oAccess[1])
#                                         wrap = [scat,""]
#         #                                 polyStmt['stmt'] = StmtExpr([StmtExpr([oMat.name]), StmtExpr(inputs, LDiv, wrap)], Assign) 
#                                         polyStmt = {}
#                                         polyStmt['stmt'] = StmtExpr(inputs, op, wrap) 
#                                         polyStmt['outinfo'] = [oMat.name, scat]
# #                                         polyStmt['domain'] = tDomain.coalesce().remove_redundancies()
#                                         polyStmt['domain'] = td
#                                         polyStmt['acc'] = False
#                                         polyStmt['oporder'] = opOrder
#                                         polyStmts.append(polyStmt)

        for r in range(len(lPinfo)):
            for c in range(len(rPInfo[0])):
                opi = oPInfo[r][c]
                for kc in range(len(lPinfo[0])):
                    lpi,rpi = lPinfo[r][kc], rPInfo[kc][c]
#                     oAccess = opi['access'].items()[0]
#                     oAccess = opi['access']
                    ldivAccess = [(lAccess,rAccess,oAccess) for lAccess in lpi['access'] for rAccess in rpi['access'] for oAccess in opi['access']]
                    ldivStruct = [(lStr,rStr) for lStr in lpi['TopLeft'].items() if issubclass(lStr[0], Triangular) for rStr in rpi['struct'].items() if rStr[0] is not ZeroMatrix ]
                    for ldStr in ldivStruct:
                        lTSDomain = self.joinAlignedSets(ldStr[0][1], lpi['tiling'], self.globalspace)
                        rTSDomain = self.joinAlignedSets(ldStr[1][1], rpi['tiling'], self.globalspace)
                        ldivDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)
                        ldivDomain = self.joinAlignedSets(ldivDomain, set_ctx, self.globalspace)
                        for ldAccess in ldivAccess:
                            oAccess = ldAccess[2]
                            oAccSet = opi['access'][oAccess] 
                            
                            mReduceDims = Map("{["+(",".join(self.indices))+"]->[i,j"+sTrailIds+"]: " + str(oAccess[2][0].of(0)) + "=i and " + str(oAccess[2][1].of(0)) + "=j}")
                            tDomainList, inputsList, opList = [], [], []
                            tDomainList, _, inputsList, _, opList, _ = \
                            self.buildBinStmtLists(expr.inexpr, (lMat, rMat), LDiv, ldivDomain, lpi, rpi, ldAccess, oAccSet, par=(True,True))

                            if tDomainList:
                                for td,inputs,op in zip(tDomainList,inputsList,opList):
                                    if not td.is_empty():
                                        tdReduced = mReduceDims.intersect_domain(td).range()
                                        tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
                                        if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
                                            fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
                                            scat = self.genGSSeq(oAccess[1])
                                            oMat2ll = oMat.toLL(sep=True) 
                                            if len(oMat2ll) > 1:
                                                wrap = [oMat2ll[1]+scat, ""]
                                            else:
                                                wrap = [scat, ""]
                                            polyStmt = {}
                                            finStmt = StmtExpr(inputs, op)
                                            finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                            polyStmt['stmt'] = StmtExpr([finStmt], None, wrap)
                                            polyStmt['domain'] = td
                                            polyStmt['acc'] = False
                                            polyStmt['outinfo'] = [oMat2ll[0], scat]
                                            polyStmts.append(polyStmt)
                                
                                
#                                 for td, inputs, op in zip(tDomainList, inputsList, opList):
#                                     if not td.is_empty():
#                                         scat = self.genGSSeq(oAccess[1])
#                                         wrap = [scat,""]
#                                         polyStmt = {}
#                                         polyStmt['stmt'] = StmtExpr(inputs, op, wrap) 
#                                         polyStmt['outinfo'] = [oMat.name, scat]
#                                         polyStmt['domain'] = td
#                                         polyStmt['acc'] = False
#                                         polyStmts.append(polyStmt)
#         
        expr.setPolyStmts(polyStmts)

#     def LDiv2(self, expr, opts):
#         
#         getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
#         getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts)
#         opOrder = self.opOrder
#         getattr(self, expr.suppExpr.__class__.__name__)(expr.suppExpr, opts)
# #         self.opOrder+=1
#         
#         blkLhs = expr.getInexprMat(0)
#         blkRhs = expr.getInexprMat(1)
#         blkOut = expr.getOut() 
#         suppBlkLhs = expr.suppExpr.getInexprMat(0)
#         suppBlkRhs = expr.suppExpr.getInexprMat(1)
#         
#         lPInfo = blkLhs.getPolyInfo(self.indices, baselevel=self.baselevel, extrainfo=['StrictLower', 'Diag', 'Tip'])
#         rPInfo = blkRhs.getPolyInfo(self.indices, baselevel=self.baselevel)
#         oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel, extrainfo=['LowerStrip'])
#         suppLPInfo = suppBlkLhs.getPolyInfo(self.indices, baselevel=self.baselevel)
#         suppRPInfo = suppBlkRhs.getPolyInfo(self.indices, baselevel=self.baselevel)
#         lMat, rMat, oMat = expr.inexpr[0].getNonTileOut(), expr.inexpr[1].getNonTileOut(), self.subsWithOut.get(expr, expr).getNonTileOut()
# 
#         accIdx = [ i for i in self.indices if i in blkLhs.idxPosAndLevInfo and blkLhs.idxPosAndLevInfo[i][2] == 1 ]
# 
#         polyStmts = []
# 
#         for r in range(len(lPInfo)):
#             for c in range(len(rPInfo[0])):
#                 opi = oPInfo[r][c]
#                 for kc in range(len(lPInfo[0])):
#                     lpi,rpi = lPInfo[r][kc], rPInfo[kc][c]
#                     oAccess = opi['access'].items()[0]
#                     ldivAccess = [(lAccess,rAccess) for lAccess in lpi['access'] for rAccess in rpi['access']]
#                     ldivStruct = [(lStr,rStr) for lStr in lpi['Tip'].items() if issubclass(lStr[0], Triangular) for rStr in rpi['struct'].items() if rStr[0] is not ZeroMatrix ]
#                     for ldStr in ldivStruct:
#                         lTSDomain = self.joinAlignedSets(ldStr[0][1], lpi['tiling'], self.globalspace)
#                         rTSDomain = self.joinAlignedSets(ldStr[1][1], rpi['tiling'], self.globalspace)
#                         ldivDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)
# 
#                         for ldAccess in ldivAccess:
#                             tDomain = self.joinAlignedSets(lpi['access'][ldAccess[0]], rpi['access'][ldAccess[1]], self.globalspace)
#                             tDomain = self.joinAlignedSets(tDomain, ldivDomain, self.globalspace)
#                             if not tDomain.is_empty():
#                                 polyStmt = {}
#                                 pssl = self.fuseStmtWithSub(tDomain, expr.inexpr[0])
#                                 if pssl:
#                                     tDomain = pssl[0][0]
#                                     lin = pssl[0][1]['stmt'].removeWrap()
#                                 else:
#                                     lin = StmtExpr([lMat.name+self.genGSSeq(ldAccess[0][1])])
#                                 pssr = self.fuseStmtWithSub(tDomain, expr.inexpr[1])
#                                 if pssr:
#                                     tDomain = pssr[0][0]
#                                     rin = pssr[0][1]['stmt'].removeWrap()
#                                 else:
#                                     rin = StmtExpr([rMat.name+self.genGSSeq(ldAccess[1][1])])
#                                 lin = StmtExpr([ lin ], wrap=['(',')']) if ldAccess[0][3] is None else StmtExpr([lin], ldAccess[0][3])                                                               
#                                 rin = StmtExpr([ rin ], wrap=['(',')']) if ldAccess[1][3] is None else StmtExpr([rin], ldAccess[1][3])
#                                 inputs = [lin, rin]
#                                 scat = self.genGSSeq(oAccess[0][1])
#                                 wrap = [scat,""]
#                                 polyStmt['stmt'] = StmtExpr(inputs, LDiv, wrap) 
#                                 polyStmt['outinfo'] = [oMat.name, scat]
#                                 polyStmt['domain'] = tDomain.coalesce().remove_redundancies()
#                                 polyStmt['acc'] = False
#                                 polyStmt['oporder'] = opOrder
#                                 polyStmts.append(polyStmt)
# 
# 
# 
#         TList = [[],[]]
#         for r in range(len(lPinfo)):
#             for c in range(len(rPInfo[0])):
#                 
#                 ts = tuple(blkRhs.getPartitionSize(r,c))
# #                 ts = (ts[0]-1, ts[1])
#                 Temp = Matrix("P"+str(globalSSAIndex()), bPInfo[r][c]['topblk'], ts)
#                 self.mDict[Temp.name] = Matrix(Temp.name, scalar, Temp.getFlatSize(), attr={ 'o':True, 'i':True, 't':True })
#                 Temp.spaceIdxNames = [ deepcopy(s) for s in blkRhs.spaceIdxNames ]
#                 if ts == (1,1):
#                     Temp.spaceIdxNames[0][0] = '0'
#                     Temp.spaceIdxNames[1][0] = '0'
#                 tPInfo = Temp.getPolyInfo(self.indices, baselevel=self.baselevel)
#                 TList[r].append((Temp, tPInfo))
#                 
#                 initDomain = self.getEmptyDomain()
# 
#                 for kc in range(len(lPinfo[0])):
#                     lpi,rpi = lPinfo[r][kc], rPInfo[kc][c]
#                     bAccess = bPInfo[r][c]['access'].items()[0]
#                     oAccess = tPInfo[0][0]['access'].items()[0]
#                     prodAccess = [(lAccess,rAccess) for lAccess in lpi['access'] for rAccess in rpi['access']]
#                     prodStruct = [(lStr,rStr) for lStr in lpi['StrictLower'].items() if lStr[0] is Matrix for rStr in rpi['struct'].items() if rStr[0] is Matrix ]
#                     lowStrip = self.getEmptyDomain() if not rpi['LowerStrip'] else rpi['LowerStrip'].items()[0][1]
#                     for pStr in prodStruct:
#                         lTSDomain = self.joinAlignedSets(pStr[0][1], lpi['tiling'], self.globalspace)
#                         rTSDomain = self.joinAlignedSets(pStr[1][1]-lowStrip, rpi['tiling'], self.globalspace)
#                         mulDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)
# 
#                         for pAccess in prodAccess:
#                             tDomain = self.joinAlignedSets(lpi['access'][pAccess[0]], rpi['access'][pAccess[1]], self.globalspace)
#                             tDomain = self.joinAlignedSets(tDomain, mulDomain, self.globalspace)
#                             if not tDomain.is_empty():
#                                 #Determine Init instances
#                                 locInitDomain = self.computeInitDomain(self.globalspace, initDomain, tDomain, [lpi['flatstruct'], rpi['flatstruct']], accIdx)
#                                 accDomain = tDomain - locInitDomain
#                                 initDomain = initDomain.union(locInitDomain).coalesce().remove_redundancies()
# 
#                                 if not locInitDomain.is_empty():
#                                     polyStmt = {}
#                                     pssl = self.fuseStmtWithSub(locInitDomain, expr.inexpr[0])
#                                     if pssl:
#                                         locInitDomain = pssl[0][0]
#                                         lin = pssl[0][1]['stmt'].removeWrap()
#                                     else:
#                                         lin = StmtExpr([lMat.name+self.genGSSeq(pAccess[0][1])])
# #                                     pssr = self.fuseStmtWithSub(locInitDomain, expr.inexpr[1])
# #                                     if pssr:
# #                                         locInitDomain = pssr[0][0]
# #                                         rin = pssr[0][1]['stmt'].removeWrap()
# #                                     else:
#                                     rin = StmtExpr([rMat.name+self.genGSSeq(pAccess[1][1])])
#                                     pssb = self.fuseStmtWithSub(locInitDomain, expr.inexpr[1])
#                                     if pssb:
#                                         locInitDomain = pssb[0][0]
#                                         b_in = pssb[0][1]['stmt'].removeWrap()
#                                     else:
#                                         b_in = StmtExpr([bMat.name+self.genGSSeq(bAccess[0][1])])
# 
#                                     
#                                     lin = StmtExpr([ lin ], wrap=['(',')']) if pAccess[0][3] is None else StmtExpr([lin], pAccess[0][3])                                                               
#                                     rin = StmtExpr([ rin ], wrap=['(',')']) if pAccess[1][3] is None else StmtExpr([rin], pAccess[1][3])                                                               
#                                     b_in = StmtExpr([ b_in ], wrap=['(',')']) if bAccess[0][3] is None else StmtExpr([b_in], bAccess[0][3])                                                               
#                                     mulin = StmtExpr([lin,rin], Mul, ["(",")"])                                          
#                                     inputs = [b_in, mulin]
#                                     scat = self.genGSSeq(oAccess[0][1])
#                                     wrap = [scat,""]
# #                                     polyStmt['stmt'] = StmtExpr([StmtExpr([Temp.name]), StmtExpr(inputs, Mul, wrap)], Assign) 
#                                     polyStmt['stmt'] = StmtExpr(inputs, Sub, wrap)
#                                     polyStmt['outinfo'] = [Temp.name, scat]
#                                     polyStmt['domain'] = locInitDomain.coalesce().remove_redundancies()
#                                     polyStmt['acc'] = False
#                                     polyStmt['oporder'] = opOrder
#                                     polyStmts.append(polyStmt)
#                                 if not accDomain.is_empty():
#                                     polyStmt = {}
#                                     pssl = self.fuseStmtWithSub(accDomain, expr.inexpr[0])
#                                     if pssl:
#                                         accDomain = pssl[0][0]
#                                         lin = pssl[0][1]['stmt'].removeWrap()
#                                     else:
#                                         lin = StmtExpr([lMat.name+self.genGSSeq(pAccess[0][1])])
# #                                     pssr = self.fuseStmtWithSub(accDomain, expr.inexpr[1])
# #                                     if pssr:
# #                                         accDomain = pssr[0][0]
# #                                         rin = pssr[0][1]['stmt'].removeWrap()
# #                                     else:
#                                     rin = StmtExpr([rMat.name+self.genGSSeq(pAccess[1][1])])
#                                     
#                                     lin = StmtExpr([ lin ], wrap=['(',')']) if pAccess[0][3] is None else StmtExpr([lin], pAccess[0][3])                                                               
#                                     rin = StmtExpr([ rin ], wrap=['(',')']) if pAccess[1][3] is None else StmtExpr([rin], pAccess[1][3])                                                               
#                                     mulin = StmtExpr([lin,rin], Mul, ["(",")"])                                          
#                                     inputs = [StmtExpr([Temp.name+self.genGSSeq(oAccess[0][1])]), mulin]
#                                     wrap = [self.genGSSeq(oAccess[0][1]),""]
#                                     polyStmt['stmt'] = StmtExpr(inputs, Sub, wrap)
#                                     polyStmt['outinfo'] = [Temp.name, self.genGSSeq(oAccess[0][1])]
#                                     polyStmt['domain'] = accDomain.coalesce().remove_redundancies()
#                                     polyStmt['acc'] = False
#                                     polyStmt['oporder'] = opOrder
#                                     polyStmts.append(polyStmt)
# 
# #         lPinfo = blkLhs.getPolyInfo(self.indices, baselevel=self.baselevel)
#         rPInfo = blkRhs.getPolyInfo(self.indices, baselevel=self.baselevel)
#         oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)
#         lMat, rMat, oMat = expr.inexpr[0].getNonTileOut(), expr.inexpr[1].getNonTileOut(), self.subsWithOut.get(expr, expr).getNonTileOut()
#         
#         for r in range(len(lPinfo)):
#             for c in range(len(rPInfo[0])):
#                 Temp, tPInfo = TList[r][c]
#                 opi = oPInfo[r][c]
#                 for kc in range(len(lPinfo[0])):
#                     lpi,rpi = lPinfo[r][kc], rPInfo[kc][c]
#                     oAccess = opi['access'].items()[0]
#                     tAccess = tPInfo[0][0]['access'].items()[0]
#                     ldivAccess = [(lAccess,rAccess) for lAccess in lpi['access'] for rAccess in rpi['access']]
#                     ldivStruct = [(lStr,rStr) for lStr in lpi['Diag'].items() for rStr in rpi['struct'].items() if rStr[0] is not ZeroMatrix ]
#                     tip = self.getEmptyDomain() if not lpi['Tip'] else lpi['Tip'].items()[0][1]
#                     for ldStr in ldivStruct:
#                         lTSDomain = self.joinAlignedSets(ldStr[0][1]-tip, lpi['tiling'], self.globalspace)
#                         rTSDomain = self.joinAlignedSets(ldStr[1][1], rpi['tiling'], self.globalspace)
#                         ldivDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)
# 
#                         for ldAccess in ldivAccess:
#                             tDomain = self.joinAlignedSets(lpi['access'][ldAccess[0]], rpi['access'][ldAccess[1]], self.globalspace)
#                             tDomain = self.joinAlignedSets(tDomain, ldivDomain, self.globalspace)
#                             if not tDomain.is_empty():
#                                 polyStmt = {}
#                                 pssl = self.fuseStmtWithSub(tDomain, expr.inexpr[0])
#                                 if pssl:
#                                     tDomain = pssl[0][0]
#                                     lin = pssl[0][1]['stmt'].removeWrap()
#                                 else:
#                                     lin = StmtExpr([lMat.name+self.genGSSeq(ldAccess[0][1])])
# #                                 pssr = self.fuseStmtWithSub(tDomain, expr.inexpr[1])
# #                                 if pssr:
# #                                     tDomain = pssr[0][0]
# #                                     rin = pssr[0][1]['stmt'].removeWrap()
# #                                 else:
#                                 rin = StmtExpr([Temp.name+self.genGSSeq(tAccess[0][1])])
#                                 lin = StmtExpr([ lin ], wrap=['(',')']) if ldAccess[0][3] is None else StmtExpr([lin], ldAccess[0][3])                                                               
# #                                 rin = StmtExpr([ rin ], wrap=['(',')']) if ldAccess[1][3] is None else StmtExpr([rin], ldAccess[1][3])
# #                                 rin = StmtExpr([rin,StmtExpr([Temp.name+self.genGSSeq(tAccess[0][1])])], Sub, ["(",")"])                                          
#                                 inputs = [lin, rin]
#                                 scat = self.genGSSeq(oAccess[0][1])
#                                 wrap = [scat,""]
# #                                 polyStmt['stmt'] = StmtExpr([StmtExpr([oMat.name]), StmtExpr(inputs, LDiv, wrap)], Assign) 
#                                 polyStmt['stmt'] = StmtExpr(inputs, LDiv, wrap) 
#                                 polyStmt['outinfo'] = [oMat.name, scat]
#                                 polyStmt['domain'] = tDomain.coalesce().remove_redundancies()
#                                 polyStmt['acc'] = False
#                                 polyStmt['oporder'] = opOrder
#                                 polyStmts.append(polyStmt)
# 
#         expr.setPolyStmts(polyStmts)

    def backward_sub(self, expr, opts):
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], opts)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], opts)
        opOrder = self.opOrder
        self.opOrder+=1
        
        blkLhs = expr.getInexprMat(0)
        blkRhs = expr.getInexprMat(1)
        blkOut = expr.getOut() 
        
        lMat, rMat = self.getNonTileMatrix(expr.inexpr[0]), self.getNonTileMatrix(self.subsWithOut.get((self.eq_id, expr), expr))
        
        lPinfo = blkLhs.getPolyInfo(self.indices, baselevel=self.baselevel, extrainfo=['StrictUpper', 'Diag', 'BottomRight'], directions=('b','b'))
        rPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel, directions=('b','f'))

        accIdx = [ i for i in self.indices if i in blkLhs.idxPosAndLevInfo and blkLhs.idxPosAndLevInfo[i][2] == 1 ]
        
        polyStmts = []
        
        TList = [[],[]]
        for r in range(len(lPinfo)):
            for c in range(len(rPInfo[0])):
                
                Temp = Matrix("P"+str(globalSSAIndex()), rPInfo[r][c]['topblk'], tuple(blkOut.getPartitionSize(r,c)) )
                self.mDict[Temp.name] = Matrix(Temp.name, scalar_block(), Temp.getFlatSize(), attr={ 'o':True, 'i':True, 't':True })
                Temp.spaceIdxNames = [ deepcopy(s) for s in blkRhs.spaceIdxNames ]
                for d in range(2):
                    if(Temp.size[d] == 1):
                        Temp.spaceIdxNames[d][0] = '0'
                tPInfo = Temp.getPolyInfo(self.indices, baselevel=self.baselevel, directions=('b','f'))
                TList[r].append((Temp, tPInfo))
                
                initDomain = self.getEmptyDomain()

                for kc in (range(len(lPinfo[0]))[::-1]):
                    lpi,rpi = lPinfo[r][kc], rPInfo[kc][c]

                    prodAccess = [(lAccess,rAccess,oAccess) for lAccess in lpi['access'] for rAccess in rpi['access'] for oAccess in tPInfo[0][0]['access']]
                    prodStruct = [(lStr,rStr) for lStr in lpi['StrictUpper'].items() if lStr[0] is Matrix for rStr in rpi['struct'].items() if rStr[0] is Matrix ]
                    for pStr in prodStruct:
                        lTSDomain = self.joinAlignedSets(pStr[0][1], lpi['tiling'], self.globalspace)
                        rTSDomain = self.joinAlignedSets(pStr[1][1], rpi['tiling'], self.globalspace)
                        mulDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)
#                         locInitDomain = self.computeInitDomain(self.globalspace, initDomain, mulDomain, [lpi['flatstruct'], rpi['flatstruct']], accIdx)
                        locInitDomain = self.computeInitDomain(self.globalspace, initDomain, mulDomain, [lTSDomain.convex_hull(), rTSDomain.convex_hull()], accIdx)
                        accDomain = mulDomain - locInitDomain
                        initDomain = initDomain.union(locInitDomain).coalesce().remove_redundancies()

                        for pAccess in prodAccess:
                            oAccess = pAccess[2]
                            oAccSet = tPInfo[0][0]['access'][oAccess] 
                            if not locInitDomain.is_empty():                                    
                                tDomainList, opList, inputsList = [], [], []
                                tDomainList, _, inputsList, _, opList, _ = \
                                self.buildBinStmtLists((expr.inexpr[0],None), (lMat, rMat), Mul, locInitDomain, lpi, rpi, pAccess, oAccSet, par=(True,True))
                                if tDomainList:
                                    for td, inputs, op in zip(tDomainList, inputsList, opList):
                                        if not td.is_empty():
                                            scat = self.genGSSeq(oAccess[1])
                                            wrap = [scat,""]
                                            polyStmt = {}
                                            finStmt = StmtExpr(inputs, op)
                                            finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                            polyStmt['stmt'] = StmtExpr([finStmt], None, wrap)
                                            polyStmt['outinfo'] = [Temp.name, scat]
                                            polyStmt['domain'] = td
                                            polyStmt['acc'] = False
                                            polyStmt['oporder'] = opOrder
                                            polyStmts.append(polyStmt)
                            if not accDomain.is_empty():
                                tDomainList, opList, inputsList = [], [], []
                                tDomainList, _, inputsList, _, opList, _ = \
                                self.buildBinStmtLists((expr.inexpr[0],None), (lMat, rMat), Mul, accDomain, lpi, rpi, pAccess, oAccSet, par=(True,True))
                                if tDomainList:
                                    for td, inputs, op in zip(tDomainList, inputsList, opList):
                                        if not td.is_empty():
                                            wrap = [self.genGSSeq(oAccess[1], acc=True),""]
                                            polyStmt = {}
                                            polyStmt['stmt'] = StmtExpr(inputs, op, wrap)
                                            polyStmt['outinfo'] = [Temp.name, self.genGSSeq(oAccess[1])]
                                            polyStmt['domain'] = td
                                            polyStmt['acc'] = True
                                            polyStmt['oporder'] = opOrder
                                            polyStmts.append(polyStmt)

        rPInfo = blkRhs.getPolyInfo(self.indices, baselevel=self.baselevel, directions=('b','f'))
        oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel, directions=('b','f'))
        lMat, rMat, oMat = self.getNonTileMatrix(expr.inexpr[0]), self.getNonTileMatrix(expr.inexpr[1]), self.subsWithOut.get((self.eq_id, expr), expr).getNonTileOut()
        
        for r in range(len(lPinfo)):
            for c in range(len(rPInfo[0])):
                Temp, tPInfo = TList[r][c]
                opi = oPInfo[r][c]
                for kc in range(len(lPinfo[0])):
                    lpi,rpi = lPinfo[r][kc], rPInfo[kc][c]
                    tAccess = tPInfo[0][0]['access'].items()[0]
                    ldivAccess = [(lAccess,rAccess,oAccess) for lAccess in lpi['access'] for rAccess in rpi['access'] for oAccess in opi['access']]
                    ldivStruct = [(lStr,rStr) for lStr in lpi['Diag'].items() for rStr in rpi['struct'].items() if rStr[0] is not ZeroMatrix ]
                    br = self.getEmptyDomain() if not lpi['BottomRight'] else lpi['BottomRight'].items()[0][1]
                    for ldStr in ldivStruct:
                        lTSDomain = self.joinAlignedSets(ldStr[0][1]-br, lpi['tiling'], self.globalspace)
                        rTSDomain = self.joinAlignedSets(ldStr[1][1], rpi['tiling'], self.globalspace)
                        ldivDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)

                        for ldAccess in ldivAccess:
                            oAccess = ldAccess[2]
                            oAccSet = opi['access'][oAccess] 
                            tDomainList, opList, inputsList = [], [], []
                            tDomainList, _, inputsList, _, opList, _ = \
                            self.buildBinStmtLists(expr.inexpr, (lMat, rMat), LDiv, ldivDomain, lpi, rpi, ldAccess, oAccSet, par=(True,True))
                            if tDomainList:
                                for td, inputs, op in zip(tDomainList, inputsList, opList):
                                    if not td.is_empty():
                                        inputs[1] = StmtExpr([inputs[1],StmtExpr([Temp.name+self.genGSSeq(tAccess[0][1])])], Sub, ["(",")"]) 
                                        scat = self.genGSSeq(oAccess[1])
                                        wrap = [scat,""]
                                        polyStmt = {}
                                        polyStmt['stmt'] = StmtExpr(inputs, op, wrap) 
                                        polyStmt['outinfo'] = [oMat.name, scat]
                                        polyStmt['domain'] = td
                                        polyStmt['acc'] = False
                                        polyStmt['oporder'] = opOrder
                                        polyStmts.append(polyStmt)

        for r in range(len(lPinfo)):
            for c in range(len(rPInfo[0])):
                opi = oPInfo[r][c]
                for kc in range(len(lPinfo[0])):
                    lpi,rpi = lPinfo[r][kc], rPInfo[kc][c]
                    ldivAccess = [(lAccess,rAccess,oAccess) for lAccess in lpi['access'] for rAccess in rpi['access'] for oAccess in opi['access']]
                    ldivStruct = [(lStr,rStr) for lStr in lpi['BottomRight'].items() if issubclass(lStr[0], Triangular) for rStr in rpi['struct'].items() if rStr[0] is not ZeroMatrix ]
                    for ldStr in ldivStruct:
                        lTSDomain = self.joinAlignedSets(ldStr[0][1], lpi['tiling'], self.globalspace)
                        rTSDomain = self.joinAlignedSets(ldStr[1][1], rpi['tiling'], self.globalspace)
                        ldivDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)

                        for ldAccess in ldivAccess:
                            oAccess = ldAccess[2]
                            oAccSet = opi['access'][oAccess] 
                            tDomainList, opList, inputsList = [], [], []
                            tDomainList, _, inputsList, _, opList, _ = \
                            self.buildBinStmtLists(expr.inexpr, (lMat, rMat), LDiv, ldivDomain, lpi, rpi, ldAccess, oAccSet, par=(True,True))
                            if tDomainList:
                                for td, inputs, op in zip(tDomainList, inputsList, opList):
                                    if not td.is_empty():
                                        scat = self.genGSSeq(oAccess[1])
                                        wrap = [scat,""]
                                        polyStmt = {}
                                        polyStmt['stmt'] = StmtExpr(inputs, op, wrap) 
                                        polyStmt['outinfo'] = [oMat.name, scat]
                                        polyStmt['domain'] = td
                                        polyStmt['acc'] = False
                                        polyStmt['oporder'] = opOrder
                                        polyStmts.append(polyStmt)
        
        expr.setPolyStmts(polyStmts)

    def Add(self, expr, ctx):
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], ctx)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], ctx)
#         opOrder = self.opOrder
#         self.opOrder+=1
        
        blkLhs = expr.getInexprMat(0)
        blkRhs = expr.getInexprMat(1)
        blkOut = self.subsWithOut.get((self.eq_id, expr), expr).getOut() 
#         blkOut = expr.getOut() 

        set_ctx = self.set_from_ctx(ctx)

        lMat, rMat = self.getNonTileMatrix(expr.inexpr[0]), self.getNonTileMatrix(expr.inexpr[1])
        oMat = self.subsWithOut.get((self.eq_id, expr), expr).getNonTileOut()
        
        lPinfo = blkLhs.getPolyInfo(self.indices, baselevel=self.baselevel)
        rPInfo = blkRhs.getPolyInfo(self.indices, baselevel=self.baselevel)
        oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)

        expr.accIds = expr.inexpr[0].accIds + expr.inexpr[1].accIds
        acc_ids=[expr.inexpr[0].accIds, expr.inexpr[1].accIds]
        sTrailIds, fullOAccSet, oAccMap = self.get_out_acc_set_and_map(expr, blkOut, ctx)
        
        polyStmts = []
        for r in range(len(lPinfo)):
            for c in range(len(lPinfo[0])):
                lpi,rpi,opi = lPinfo[r][c], rPInfo[r][c], oPInfo[r][c]
                addAccess = [(lAccess,rAccess,oAccess) for lAccess in lpi['access'] for rAccess in rpi['access'] for oAccess in opi['access']]
                addStruct = [(lStr,rStr,oStr) for lStr in lpi['struct'].items() for rStr in rpi['struct'].items() if (lStr[0] is not ZeroMatrix or (lStr[0] is ZeroMatrix and rStr[0] is not ZeroMatrix)) \
                             for oStr in opi['struct'].items() if not issubclass(oStr[0], ConstantMatrix) ]
                for aStr in addStruct:
                    addDomain = self.joinAlignedSets(aStr[0][1], aStr[1][1], self.globalspace)
                    addDomain = self.joinAlignedSets(addDomain, aStr[2][1], self.globalspace)
                    addDomain = self.joinAlignedSets(addDomain, lpi['tiling'], self.globalspace)
                    addDomain = self.joinAlignedSets(addDomain, set_ctx, self.globalspace)
                    if addDomain.is_empty():
                        continue
                    for aAccess in addAccess:
                        oAccess = aAccess[2]
                        oAccSet = opi['access'][oAccess] 
                        mReduceDims = Map("{["+(",".join(self.indices))+"]->[i,j"+sTrailIds+"]: " + str(oAccess[2][0].of(0)) + "=i and " + str(oAccess[2][1].of(0)) + "=j}")
                        tDomainList, inputsList, opList = [], [], []
                        acc_data = []
                        tAccDomainList, accInputsList, accOpList = [], [], []
                        if aStr[0][0] is ZeroMatrix:
                            tDomainList, tAccDomainList, inputsList, accInputsList, opList, accOpList = \
                            self.buildUnStmtLists(expr.inexpr[1], rMat, None, addDomain, rpi, aAccess[1], oAccSet, mReduceDims, oAccMap, includeAccPss=True)
                            acc_data.append( (tAccDomainList, accInputsList, accOpList) )
                        elif aStr[1][0] is ZeroMatrix:
                            tDomainList, tAccDomainList, inputsList, accInputsList, opList, accOpList = \
                            self.buildUnStmtLists(expr.inexpr[0], lMat, None, addDomain, lpi, aAccess[0], oAccSet, mReduceDims, oAccMap, includeAccPss=True)
                            acc_data.append( (tAccDomainList, accInputsList, accOpList) )
                        else:
                            tDomainList, _, inputsList, _, opList, _ = \
                            self.buildBinStmtLists(expr.inexpr, (lMat, rMat), Add, addDomain, lpi, rpi, aAccess, oAccSet, mReduceDims, oAccMap, acc_ids=acc_ids)
                            # We split the build as in some areas where l/r is not defined r/l may be. 
                            _, tAccDomainList, _, accInputsList, _, accOpList = \
                            self.buildUnStmtLists(expr.inexpr[0], lMat, None, addDomain, lpi, aAccess[0], oAccSet, mReduceDims, oAccMap, includeAccPss=True, pos=0, acc_ids=acc_ids)
                            acc_data.append( (tAccDomainList, accInputsList, accOpList) )
                            _, tAccDomainList, _, accInputsList, _, accOpList = \
                            self.buildUnStmtLists(expr.inexpr[1], rMat, None, addDomain, rpi, aAccess[1], oAccSet, mReduceDims, oAccMap, includeAccPss=True, pos=1, acc_ids=acc_ids)
                            acc_data.append( (tAccDomainList, accInputsList, accOpList) )
                        if tDomainList:
                            for td,inputs,op in zip(tDomainList,inputsList,opList):
                                if not td.is_empty():
                                    tdReduced = mReduceDims.intersect_domain(td).range()
                                    tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()

                                    overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                    polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                    if new_ps:
                                        polyStmt['touched'] = tdTransformedByOAcc
                                        polyStmt['reducedims'] = mReduceDims 
                                        polyStmt['stmt'] = []
                                        polyStmt['perm_oacc'] = []
                                        polyStmt['domain'] = []
                                        polyStmt['outinfo'] = []
                                    scat = self.genGSSeq(oAccess[1])
                                    oMat2ll = oMat.toLL(sep=True) 
                                    if len(oMat2ll) > 1:
                                        wrap = [oMat2ll[1]+scat, ""]
                                    else:
                                        wrap = [scat, ""]
                                    finStmt = StmtExpr(inputs, op)
                                    finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                    polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                    polyStmt['perm_oacc'].append( oAccess[3] )
                                    polyStmt['domain'].append( td )
                                    polyStmt['acc'] = False
                                    polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                    if new_ps:
                                        polyStmts.append(polyStmt)

                        while acc_data:
                            acc_triple = acc_data.pop()
                            if acc_triple[0]:
                                for td,inputs,op in zip(*acc_triple):
                                    if not td.is_empty():
                                        tdReduced = mReduceDims.intersect_domain(td).range()
                                        tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
                                        overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                        polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                        if new_ps:
                                            polyStmt['touched'] = tdTransformedByOAcc
                                            polyStmt['reducedims'] = mReduceDims 
                                            polyStmt['stmt'] = []
                                            polyStmt['perm_oacc'] = []
                                            polyStmt['domain'] = []
                                            polyStmt['outinfo'] = []
                                        scat = self.genGSSeq(oAccess[1])
                                        oMat2ll = oMat.toLL(acc=True, sep=True) 
                                        if len(oMat2ll) > 1:
                                            wrap = ["$"+oMat2ll[1]+self.genGSSeq(oAccess[1], acc=True), ""]
                                        else:
                                            wrap = [self.genGSSeq(oAccess[1], acc=True),""]
                                        finStmt = StmtExpr(inputs, op)
                                        finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                        polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                        polyStmt['perm_oacc'].append( oAccess[3] )
                                        polyStmt['domain'].append( td )
                                        polyStmt['acc'] = True
                                        polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                        if new_ps:
                                            polyStmts.append(polyStmt)
                        
        expr.setPolyStmts(polyStmts)

    def Sub(self, expr, ctx):
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], ctx)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], ctx)
        
        blkLhs = expr.getInexprMat(0)
        blkRhs = expr.getInexprMat(1)
#         blkOut = expr.getOut() 
        blkOut = self.subsWithOut.get((self.eq_id, expr), expr).getOut() 

        set_ctx = self.set_from_ctx(ctx)

        lMat, rMat = self.getNonTileMatrix(expr.inexpr[0]), self.getNonTileMatrix(expr.inexpr[1])
        oMat = self.subsWithOut.get((self.eq_id, expr), expr).getNonTileOut()
        
        lPinfo = blkLhs.getPolyInfo(self.indices, baselevel=self.baselevel)
        rPInfo = blkRhs.getPolyInfo(self.indices, baselevel=self.baselevel)
        oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)

        expr.accIds = expr.inexpr[0].accIds + expr.inexpr[1].accIds
        acc_ids=[expr.inexpr[0].accIds, expr.inexpr[1].accIds]
        sTrailIds, fullOAccSet, oAccMap = self.get_out_acc_set_and_map(expr, blkOut, ctx)
        
        polyStmts = []
        for r in range(len(lPinfo)):
            for c in range(len(lPinfo[0])):
                lpi,rpi,opi = lPinfo[r][c], rPInfo[r][c], oPInfo[r][c]
                subAccess = [(lAccess,rAccess,oAccess) for lAccess in lpi['access'] for rAccess in rpi['access'] for oAccess in opi['access']]
                subStruct = [(lStr,rStr, oStr) for lStr in lpi['struct'].items() for rStr in rpi['struct'].items() for oStr in opi['struct'].items() \
                             if not (lStr[0] is ZeroMatrix and rStr[0] is ZeroMatrix or issubclass(oStr[0], ConstantMatrix)) ]
                for aStr in subStruct:
                    subDomain = self.joinAlignedSets(aStr[0][1], aStr[1][1], self.globalspace)
                    subDomain = self.joinAlignedSets(subDomain, aStr[2][1], self.globalspace)
                    subDomain = self.joinAlignedSets(subDomain, lpi['tiling'], self.globalspace)
                    subDomain = self.joinAlignedSets(subDomain, set_ctx, self.globalspace)
                    for sAccess in subAccess:
                        oAccess = sAccess[2]
                        oAccSet = opi['access'][oAccess] 
                        mReduceDims = Map("{["+(",".join(self.indices))+"]->[i,j"+sTrailIds+"]: " + str(oAccess[2][0].of(0)) + "=i and " + str(oAccess[2][1].of(0)) + "=j}")
                        tDomainList, inputsList, opList = [], [], []
                        acc_data = []
                        tAccDomainList, accInputsList, accOpList = [], [], []

                        tDomainList, _, inputsList, _, opList, _ = \
                        self.buildBinStmtLists(expr.inexpr, (lMat, rMat), Sub, subDomain, lpi, rpi, sAccess, oAccSet, mReduceDims, oAccMap, par=[False,True], acc_ids=acc_ids)

                        _, tAccDomainList, _, accInputsList, _, accOpList = \
                        self.buildUnStmtLists(expr.inexpr[0], lMat, None, subDomain, lpi, sAccess[0], oAccSet, mReduceDims, oAccMap, includeAccPss=True, pos=0, acc_ids=acc_ids)
                        acc_data.append( (tAccDomainList, accInputsList, accOpList) )
                        _, tAccDomainList, _, accInputsList, _, accOpList = \
                        self.buildUnStmtLists(expr.inexpr[1], rMat, Neg, subDomain, rpi, sAccess[1], oAccSet, mReduceDims, oAccMap, includeAccPss=True, par=True, pos=1, acc_ids=acc_ids)
                        acc_data.append( (tAccDomainList, accInputsList, accOpList) )
                        
                        if tDomainList:
                            for td,inputs,op in zip(tDomainList,inputsList,opList):
                                if not td.is_empty():
                                    tdReduced = mReduceDims.intersect_domain(td).range()
                                    tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
                                    overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                    polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                    if new_ps:
                                        polyStmt['touched'] = tdTransformedByOAcc
                                        polyStmt['reducedims'] = mReduceDims 
                                        polyStmt['stmt'] = []
                                        polyStmt['perm_oacc'] = []
                                        polyStmt['domain'] = []
                                        polyStmt['outinfo'] = []
                                    scat = self.genGSSeq(oAccess[1])
                                    oMat2ll = oMat.toLL(sep=True) 
                                    if len(oMat2ll) > 1:
                                        wrap = [oMat2ll[1]+scat, ""]
                                    else:
                                        wrap = [scat, ""]
                                    finStmt = StmtExpr(inputs, op)
                                    finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                    polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                    polyStmt['perm_oacc'].append( oAccess[3] )
                                    polyStmt['domain'].append( td )
                                    polyStmt['acc'] = False
                                    polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                    if new_ps:
                                        polyStmts.append(polyStmt)
                        
                        while acc_data:
                            acc_triple = acc_data.pop()
                            if acc_triple[0]:
                                for td,inputs,op in zip(*acc_triple):
                                    if not td.is_empty():
                                        tdReduced = mReduceDims.intersect_domain(td).range()
                                        tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
                                        overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                        polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                        if new_ps:
                                            polyStmt['touched'] = tdTransformedByOAcc
                                            polyStmt['reducedims'] = mReduceDims 
                                            polyStmt['stmt'] = []
                                            polyStmt['perm_oacc'] = []
                                            polyStmt['domain'] = []
                                            polyStmt['outinfo'] = []
                                        scat = self.genGSSeq(oAccess[1])
                                        oMat2ll = oMat.toLL(acc=True, sep=True) 
                                        if len(oMat2ll) > 1:
                                            wrap = ["$"+oMat2ll[1]+self.genGSSeq(oAccess[1], acc=True), ""]
                                        else:
                                            wrap = [self.genGSSeq(oAccess[1], acc=True),""]
                                        finStmt = StmtExpr(inputs, op)
                                        finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                        polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                        polyStmt['perm_oacc'].append( oAccess[3] )
                                        polyStmt['domain'].append( td )
                                        polyStmt['acc'] = True
                                        polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                        if new_ps:
                                            polyStmts.append(polyStmt)
        
        expr.setPolyStmts(polyStmts)

    def Neg(self, expr, ctx):
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], ctx)
        
        blkSub = expr.getInexprMat(0)
        blkOut = self.subsWithOut.get((self.eq_id, expr), expr).getOut() 
#         blkOut = expr.getOut() 

        set_ctx = self.set_from_ctx(ctx)

        subMat = self.getNonTileMatrix(expr.inexpr[0])
        oMat = self.subsWithOut.get((self.eq_id, expr), expr).getNonTileOut()
        
        sPinfo = blkSub.getPolyInfo(self.indices, baselevel=self.baselevel)
        oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)

        expr.accIds = expr.inexpr[0].accIds
        sTrailIds, fullOAccSet, oAccMap = self.get_out_acc_set_and_map(expr, blkOut, ctx)
        
        polyStmts = []
        for r in range(len(sPinfo)):
            for c in range(len(sPinfo[0])):
                spi,opi = sPinfo[r][c], oPInfo[r][c]
                negAccess = [(sAccess,oAccess) for sAccess in spi['access'] for oAccess in opi['access']]
                negStruct = [ (sStr,oStr) for sStr in spi['struct'].items() if not (sStr[0] is ZeroMatrix) for oStr in opi['struct'].items() if not issubclass(oStr[0], ConstantMatrix) ]
                for nStr in negStruct:
                    negDomain = self.joinAlignedSets(nStr[0][1], spi['tiling'], self.globalspace)
                    negDomain = self.joinAlignedSets(negDomain, nStr[1][1], self.globalspace)
                    negDomain = self.joinAlignedSets(negDomain, set_ctx, self.globalspace)
                    for nAccess in negAccess:
                        oAccess = nAccess[1]
                        oAccSet = opi['access'][oAccess] 
                        mReduceDims = Map("{["+(",".join(self.indices))+"]->[i,j"+sTrailIds+"]: " + str(oAccess[2][0].of(0)) + "=i and " + str(oAccess[2][1].of(0)) + "=j}")
                        tDomainList, inputsList, opList = [], [], []
                        tAccDomainList, accInputsList, accOpList = [], [], []

                        tDomainList, tAccDomainList, inputsList, accInputsList, opList, accOpList = \
                        self.buildUnStmtLists(expr.inexpr[0], subMat, Neg, negDomain, spi, nAccess[0], oAccSet, mReduceDims, oAccMap, includeAccPss=True, par=True)

                        if tDomainList:
                            for td,inputs,op in zip(tDomainList,inputsList,opList):
                                if not td.is_empty():
                                    tdReduced = mReduceDims.intersect_domain(td).range()
                                    tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
#                                     if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
#                                         fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
#                                         polyStmt = {}
                                    overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                    polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                    if new_ps:
                                        polyStmt['touched'] = tdTransformedByOAcc
                                        polyStmt['reducedims'] = mReduceDims 
                                        polyStmt['stmt'] = []
                                        polyStmt['perm_oacc'] = []
                                        polyStmt['domain'] = []
                                        polyStmt['outinfo'] = []
                                    scat = self.genGSSeq(oAccess[1])
                                    oMat2ll = oMat.toLL(sep=True) 
                                    if len(oMat2ll) > 1:
                                        wrap = [oMat2ll[1]+scat, ""]
                                    else:
                                        wrap = [scat, ""]
                                    finStmt = StmtExpr(inputs, op)
                                    finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                    polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                    polyStmt['perm_oacc'].append( oAccess[3] )
                                    polyStmt['domain'].append( td )
                                    polyStmt['acc'] = False
                                    polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                    if new_ps:
                                        polyStmts.append(polyStmt)
                        if tAccDomainList:
                            for td,inputs,op in zip(tAccDomainList, accInputsList, accOpList):
                                if not td.is_empty():
                                    tdReduced = mReduceDims.intersect_domain(td).range()
                                    tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
#                                     if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
#                                         fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
#                                         polyStmt = {}
                                    overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                    polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                    if new_ps:
                                        polyStmt['touched'] = tdTransformedByOAcc
                                        polyStmt['reducedims'] = mReduceDims 
                                        polyStmt['stmt'] = []
                                        polyStmt['perm_oacc'] = []
                                        polyStmt['domain'] = []
                                        polyStmt['outinfo'] = []
                                    scat = self.genGSSeq(oAccess[1])
                                    oMat2ll = oMat.toLL(acc=True, sep=True) 
                                    if len(oMat2ll) > 1:
                                        wrap = ["$"+oMat2ll[1]+self.genGSSeq(oAccess[1], acc=True), ""]
                                    else:
                                        wrap = [self.genGSSeq(oAccess[1], acc=True),""]
                                    finStmt = StmtExpr(inputs, op)
                                    finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                    polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                    polyStmt['perm_oacc'].append( oAccess[3] )
                                    polyStmt['domain'].append( td )
                                    polyStmt['acc'] = True
                                    polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                    if new_ps:
                                        polyStmts.append(polyStmt)
        
        expr.setPolyStmts(polyStmts)
        
    def Sqrt(self, expr, ctx):
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], ctx)
        
        blkSub = expr.getInexprMat(0)
        blkOut = self.subsWithOut.get((self.eq_id, expr), expr).getOut()
#         blkOut = expr.getOut()

        set_ctx = self.set_from_ctx(ctx)
        
        subMat = self.getNonTileMatrix(expr.inexpr[0])
        oMat = self.subsWithOut.get((self.eq_id, expr), expr).getNonTileOut()

        subPinfo = blkSub.getPolyInfo(self.indices, baselevel=self.baselevel)
        oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)

        expr.accIds = expr.inexpr[0].accIds
        sTrailIds, fullOAccSet, oAccMap = self.get_out_acc_set_and_map(expr, blkOut, ctx)
        
        polyStmts = []
        spi,opi = subPinfo[0][0], oPInfo[0][0]
        srAccess = [ (sAccess, oAccess) for sAccess in spi['access'] for oAccess in opi['access'] ]
        srStruct = [ (sStr,oStr) for sStr in spi['struct'].items() for oStr in opi['struct'].items() if not issubclass(oStr[0], ConstantMatrix) ]
        for srStr in srStruct:
            srDomain = self.joinAlignedSets(srStr[0][1], spi['tiling'], self.globalspace)
            srDomain = self.joinAlignedSets(srDomain, srStr[1][1], self.globalspace)
            srDomain = self.joinAlignedSets(srDomain, set_ctx, self.globalspace)
            for tAccess in srAccess:
                oAccess = tAccess[1]
                oAccSet = opi['access'][oAccess] 
                mReduceDims = Map("{["+(",".join(self.indices))+"]->[i,j"+sTrailIds+"]: " + str(oAccess[2][0].of(0)) + "=i and " + str(oAccess[2][1].of(0)) + "=j}")
                tDomainList, inputsList, opList = [], [], []
                tDomainList, _, inputsList, _, opList, _ = \
                self.buildUnStmtLists(expr.inexpr[0], subMat, Sqrt, srDomain, spi, tAccess[0], oAccSet, mReduceDims, oAccMap)

                if tDomainList:
                    for td,inputs,op in zip(tDomainList,inputsList,opList):
                        if not td.is_empty():
                            tdReduced = mReduceDims.intersect_domain(td).range()
                            tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
#                             if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
#                                 fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
#                                 polyStmt = {}
                            overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                            polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                            if new_ps:
                                polyStmt['touched'] = tdTransformedByOAcc
                                polyStmt['reducedims'] = mReduceDims 
                                polyStmt['stmt'] = []
                                polyStmt['perm_oacc'] = []
                                polyStmt['domain'] = []
                                polyStmt['outinfo'] = []
                            scat = self.genGSSeq(oAccess[1])
                            oMat2ll = oMat.toLL(sep=True) 
                            if len(oMat2ll) > 1:
                                wrap = [oMat2ll[1]+scat, ""]
                            else:
                                wrap = [scat, ""]
                            finStmt = StmtExpr(inputs, op)
                            finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                            polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                            polyStmt['perm_oacc'].append( oAccess[3] )
                            polyStmt['domain'].append( td )
                            polyStmt['acc'] = False
                            polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                            if new_ps:
                                polyStmts.append(polyStmt)

        expr.setPolyStmts(polyStmts)
    
    def Div(self, expr, ctx):
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], ctx)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], ctx)
        
        blkLhs = expr.getInexprMat(0)
        blkRhs = expr.getInexprMat(1)
        blkOut = self.subsWithOut.get((self.eq_id, expr), expr).getOut() 
#         blkOut = expr.getOut() 

        set_ctx = self.set_from_ctx(ctx)

        lMat, rMat = self.getNonTileMatrix(expr.inexpr[0]), self.getNonTileMatrix(expr.inexpr[1])
        oMat = self.subsWithOut.get((self.eq_id, expr), expr).getNonTileOut()
        
        lPinfo = blkLhs.getPolyInfo(self.indices, baselevel=self.baselevel)
        rPInfo = blkRhs.getPolyInfo(self.indices, baselevel=self.baselevel)
        oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)

        expr.accIds = expr.inexpr[0].accIds + expr.inexpr[1].accIds
        acc_ids = [expr.inexpr[0].accIds, expr.inexpr[1].accIds]
        sTrailIds, fullOAccSet, oAccMap = self.get_out_acc_set_and_map(expr, blkOut, ctx)
        
        polyStmts = []
        lpi,rpi,opi = lPinfo[0][0], rPInfo[0][0], oPInfo[0][0]
        divAccess = [(lAccess,rAccess,oAccess) for lAccess in lpi['access'] for rAccess in rpi['access'] for oAccess in opi['access']]
        divStruct = [(lStr,rStr,oStr) for lStr in lpi['struct'].items() for rStr in rpi['struct'].items() if not (lStr[0] is ZeroMatrix or rStr[0] is ZeroMatrix) \
                      for oStr in opi['struct'].items() if not issubclass(oStr[0], ConstantMatrix) ]
        for dStr in divStruct:
            lTSDomain = self.joinAlignedSets(dStr[0][1], lpi['tiling'], self.globalspace)
            rTSDomain = self.joinAlignedSets(dStr[1][1], rpi['tiling'], self.globalspace)
            divDomain = self.joinAlignedSets(lTSDomain, rTSDomain, self.globalspace)
            divDomain = self.joinAlignedSets(divDomain, dStr[2][1], self.globalspace)
            divDomain = self.joinAlignedSets(divDomain, set_ctx, self.globalspace)
            for rdAccess in divAccess:
                oAccess = rdAccess[2]
                oAccSet = opi['access'][oAccess] 
                mReduceDims = Map("{["+(",".join(self.indices))+"]->[i,j"+sTrailIds+"]: " + str(oAccess[2][0].of(0)) + "=i and " + str(oAccess[2][1].of(0)) + "=j}")
                tDomainList, inputsList, opList = [], [], []

                tDomainList, _, inputsList, _, opList, _ = \
                self.buildBinStmtLists(expr.inexpr, (lMat, rMat), Div, divDomain, lpi, rpi, rdAccess, oAccSet, mReduceDims, oAccMap, par=(True,True), acc_ids=acc_ids)

                if tDomainList:
                    for td,inputs,op in zip(tDomainList,inputsList,opList):
                        if not td.is_empty():
                            tdReduced = mReduceDims.intersect_domain(td).range()
                            tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
#                             if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
#                                 fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
#                                 polyStmt = {}
                            overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                            polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                            if new_ps:
                                polyStmt['touched'] = tdTransformedByOAcc
                                polyStmt['reducedims'] = mReduceDims 
                                polyStmt['stmt'] = []
                                polyStmt['perm_oacc'] = []
                                polyStmt['domain'] = []
                                polyStmt['outinfo'] = []
                            scat = self.genGSSeq(oAccess[1])
                            oMat2ll = oMat.toLL(sep=True) 
                            if len(oMat2ll) > 1:
                                wrap = [oMat2ll[1]+scat, ""]
                            else:
                                wrap = [scat, ""]
                            finStmt = StmtExpr(inputs, op)
                            finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                            polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                            polyStmt['perm_oacc'].append( oAccess[3] )
                            polyStmt['domain'].append( td )
                            polyStmt['acc'] = False
                            polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                            if new_ps:
                                polyStmts.append(polyStmt)
        
        expr.setPolyStmts(polyStmts)

    def Kro(self, expr, ctx):
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], ctx)
        getattr(self, expr.inexpr[1].__class__.__name__)(expr.inexpr[1], ctx)

        blkLhs = expr.getInexprMat(0)
        blkRhs = expr.getInexprMat(1)
        blkSca, blkMat, scaLhs = (blkLhs, blkRhs, True) if blkLhs.isScalar() else (blkRhs, blkLhs, False)
        blkOut = self.subsWithOut.get((self.eq_id, expr), expr).getOut() 
#         blkOut = expr.getOut() 

        set_ctx = self.set_from_ctx(ctx)
        
        lMat, rMat = self.getNonTileMatrix(expr.inexpr[0]), self.getNonTileMatrix(expr.inexpr[1])
        oMat = self.subsWithOut.get((self.eq_id, expr), expr).getNonTileOut()
        
        scaPinfo = blkSca.getPolyInfo(self.indices, baselevel=self.baselevel)
        matPInfo = blkMat.getPolyInfo(self.indices, baselevel=self.baselevel)
        oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)

        expr.accIds = expr.inexpr[0].accIds + expr.inexpr[1].accIds
        acc_ids=[expr.inexpr[0].accIds, expr.inexpr[1].accIds]
        sTrailIds, fullOAccSet, oAccMap = self.get_out_acc_set_and_map(expr, blkOut, ctx)
        
        polyStmts = []
        spi = scaPinfo[0][0]
        for r in range(len(matPInfo)):
            for c in range(len(matPInfo[0])):
                mpi,opi = matPInfo[r][c], oPInfo[r][c]
                kroAccess = [(scaAccess,mAccess,oAccess) for scaAccess in spi['access'] for mAccess in mpi['access'] for oAccess in opi['access']]
                scamulStruct = [ (scaStr,mStr,oStr) for scaStr in spi['struct'].items() for mStr in mpi['struct'].items() if scaStr[0] is not ZeroMatrix and mStr[0] is not ZeroMatrix \
                                for oStr in opi['struct'].items() if not issubclass(oStr[0], ConstantMatrix) ]
                for smStr in scamulStruct:
                    scaTSDomain = self.joinAlignedSets(smStr[0][1], spi['tiling'], self.globalspace)
                    matTSDomain = self.joinAlignedSets(smStr[1][1], mpi['tiling'], self.globalspace)
                    scamulDomain = self.joinAlignedSets(scaTSDomain, matTSDomain, self.globalspace)
                    scamulDomain = self.joinAlignedSets(scamulDomain, smStr[2][1], self.globalspace)
                    scamulDomain = self.joinAlignedSets(scamulDomain, set_ctx, self.globalspace)
                    for tAccess in kroAccess:
                        kAccess = (tAccess[0], tAccess[1]) if scaLhs else (tAccess[1], tAccess[0])
                        oAccess = tAccess[2]
                        oAccSet = opi['access'][oAccess] 
                        lpi, rpi = (spi, mpi) if scaLhs else (mpi, spi) 
                        mReduceDims = Map("{["+(",".join(self.indices))+"]->[i,j"+sTrailIds+"]: " + str(oAccess[2][0].of(0)) + "=i and " + str(oAccess[2][1].of(0)) + "=j}")
                        tDomainList, inputsList, opList = [], [], []
                        tAccDomainList, accInputsList, accOpList = [], [], []
                        tDomainList, tAccDomainList, inputsList, accInputsList, opList, accOpList = \
                        self.buildBinStmtLists(expr.inexpr, (lMat, rMat), Kro, scamulDomain, lpi, rpi, kAccess, oAccSet, mReduceDims, oAccMap, includeAccPss=(True, True), par=(True,True), acc_ids=acc_ids)
                        if tDomainList:
                            for td,inputs,op in zip(tDomainList,inputsList,opList):
                                if not td.is_empty():
                                    tdReduced = mReduceDims.intersect_domain(td).range()
                                    tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()

                                    overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                    polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                    if new_ps:
                                        polyStmt['touched'] = tdTransformedByOAcc
                                        polyStmt['reducedims'] = mReduceDims 
                                        polyStmt['stmt'] = []
                                        polyStmt['perm_oacc'] = []
                                        polyStmt['domain'] = []
                                        polyStmt['outinfo'] = []
                                    scat = self.genGSSeq(oAccess[1])
                                    oMat2ll = oMat.toLL(sep=True) 
                                    if len(oMat2ll) > 1:
                                        wrap = [oMat2ll[1]+scat, ""]
                                    else:
                                        wrap = [scat, ""]
                                    finStmt = StmtExpr(inputs, op)
                                    finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                    polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                    polyStmt['perm_oacc'].append( oAccess[3] )
                                    polyStmt['domain'].append( td )
                                    polyStmt['acc'] = False
                                    polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                    if new_ps:
                                        polyStmts.append(polyStmt)
                        if tAccDomainList:
                            for td,inputs,op in zip(tAccDomainList, accInputsList, accOpList):
                                if not td.is_empty():
                                    tdReduced = mReduceDims.intersect_domain(td).range()
                                    tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
#                                     if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
#                                         fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
#                                         polyStmt = {}
                                    overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                    polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                    if new_ps:
                                        polyStmt['touched'] = tdTransformedByOAcc
                                        polyStmt['reducedims'] = mReduceDims 
                                        polyStmt['stmt'] = []
                                        polyStmt['perm_oacc'] = []
                                        polyStmt['domain'] = []
                                        polyStmt['outinfo'] = []
                                    scat = self.genGSSeq(oAccess[1])
                                    oMat2ll = oMat.toLL(acc=True, sep=True) 
                                    if len(oMat2ll) > 1:
                                        wrap = ["$"+oMat2ll[1]+self.genGSSeq(oAccess[1], acc=True), ""]
                                    else:
                                        wrap = [self.genGSSeq(oAccess[1], acc=True),""]
                                    finStmt = StmtExpr(inputs, op)
                                    finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                    polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                    polyStmt['perm_oacc'].append( oAccess[3] )
                                    polyStmt['domain'].append( td )
                                    polyStmt['acc'] = True
                                    polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                    if new_ps:
                                        polyStmts.append(polyStmt)

        expr.setPolyStmts(polyStmts)

    def T(self, expr, ctx):
        
        getattr(self, expr.inexpr[0].__class__.__name__)(expr.inexpr[0], ctx)
        
        blkSub = expr.getInexprMat(0)
        blkOut = self.subsWithOut.get((self.eq_id, expr), expr).getOut() 
#         blkOut = expr.getOut() 

        set_ctx = self.set_from_ctx(ctx)
        
        subMat = self.getNonTileMatrix(expr.inexpr[0])
        oMat = self.subsWithOut.get((self.eq_id, expr), expr).getNonTileOut()

        subPinfo = blkSub.getPolyInfo(self.indices, baselevel=self.baselevel)
        oPInfo = blkOut.getPolyInfo(self.indices, baselevel=self.baselevel)

        expr.accIds = expr.inexpr[0].accIds
        sTrailIds, fullOAccSet, oAccMap = self.get_out_acc_set_and_map(expr, blkOut, ctx)
        
        polyStmts = []
        for r in range(len(subPinfo)):
            for c in range(len(subPinfo[0])):
                spi,opi = subPinfo[r][c], oPInfo[c][r]
                trAccess = [ (sAccess, oAccess) for sAccess in spi['access'] for oAccess in opi['access'] ]
                trStruct = [ (sStr,oStr) for sStr in spi['struct'].items() if not issubclass(sStr[0], AllEntriesConstantMatrix) for oStr in opi['struct'].items() if not issubclass(oStr[0], ConstantMatrix) ]
                for trStr in trStruct:
                    trDomain = self.joinAlignedSets(trStr[0][1], spi['tiling'], self.globalspace)
                    trDomain = self.joinAlignedSets(trDomain, trStr[1][1], self.globalspace)
                    trDomain = self.joinAlignedSets(trDomain, set_ctx, self.globalspace)
                    if trDomain.is_empty():
                        continue
                    for tAccess in trAccess:
                        oAccess = tAccess[1]
                        oAccSet = opi['access'][oAccess] 
                        mReduceDims = Map("{["+(",".join(self.indices))+"]->[i,j"+sTrailIds+"]: " + str(oAccess[2][0].of(0)) + "=i and " + str(oAccess[2][1].of(0)) + "=j}")
                        tDomainList, inputsList, opList = [], [], []
                        tAccDomainList, accInputsList, accOpList = [], [], []
                        tDomainList, tAccDomainList, inputsList, accInputsList, opList, accOpList = \
                        self.buildUnStmtLists(expr.inexpr[0], subMat, T, trDomain, spi, tAccess[0], oAccSet, mReduceDims, oAccMap, includeAccPss=True, par=True)

                        if tDomainList:
                            for td,inputs,op in zip(tDomainList,inputsList,opList):
                                if not td.is_empty():
                                    tdReduced = mReduceDims.intersect_domain(td).range()
                                    tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
#                                     if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
#                                         fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
#                                         polyStmt = {}
                                    overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                    polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                    if new_ps:
                                        polyStmt['touched'] = tdTransformedByOAcc
                                        polyStmt['reducedims'] = mReduceDims 
                                        polyStmt['stmt'] = []
                                        polyStmt['perm_oacc'] = []
                                        polyStmt['domain'] = []
                                        polyStmt['outinfo'] = []
                                    scat = self.genGSSeq(oAccess[1])
                                    oMat2ll = oMat.toLL(sep=True) 
                                    if len(oMat2ll) > 1:
                                        wrap = [oMat2ll[1]+scat, ""]
                                    else:
                                        wrap = [scat, ""]
                                    finStmt = StmtExpr(inputs, op)
                                    finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                    polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                    polyStmt['perm_oacc'].append( oAccess[3] )
                                    polyStmt['domain'].append( td )
                                    polyStmt['acc'] = False
                                    polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                    if new_ps:
                                        polyStmts.append(polyStmt)

                        if tAccDomainList:
                            for td,inputs,op in zip(tAccDomainList, accInputsList, accOpList):
                                if not td.is_empty():
                                    tdReduced = mReduceDims.intersect_domain(td).range()
                                    tdTransformedByOAcc = oAccMap.intersect_domain(tdReduced).range()
#                                     if fullOAccSet.intersect(tdTransformedByOAcc).is_empty():
#                                         fullOAccSet = fullOAccSet.union(tdTransformedByOAcc)
#                                         polyStmt = {}
                                    overlapping_ps = filter(lambda ps: tdTransformedByOAcc == ps['touched'], polyStmts)
                                    polyStmt, new_ps = (overlapping_ps[0], False) if overlapping_ps else ({}, True) 
                                    if new_ps:
                                        polyStmt['touched'] = tdTransformedByOAcc
                                        polyStmt['reducedims'] = mReduceDims 
                                        polyStmt['stmt'] = []
                                        polyStmt['perm_oacc'] = []
                                        polyStmt['domain'] = []
                                        polyStmt['outinfo'] = []
                                    scat = self.genGSSeq(oAccess[1])
                                    oMat2ll = oMat.toLL(acc=True, sep=True) 
                                    if len(oMat2ll) > 1:
                                        wrap = ["$"+oMat2ll[1]+self.genGSSeq(oAccess[1], acc=True), ""]
                                    else:
                                        wrap = [self.genGSSeq(oAccess[1], acc=True),""]
                                    finStmt = StmtExpr(inputs, op)
                                    finStmt = finStmt if oAccess[3] is None else StmtExpr([finStmt], oAccess[3].inverse())
                                    polyStmt['stmt'].append( StmtExpr([finStmt], None, wrap) )
                                    polyStmt['perm_oacc'].append( oAccess[3] )
                                    polyStmt['domain'].append( td )
                                    polyStmt['acc'] = True
                                    polyStmt['outinfo'].append( [oMat2ll[0], scat] )
                                    if new_ps:
                                        polyStmts.append(polyStmt)

        expr.setPolyStmts(polyStmts)

    def Tile(self, expr, opts):
        pass

    def G(self, expr, opts):
        pass

    def Scalar(self, expr, opts):
        pass

    def SquaredMatrix(self, expr, opts):
        pass
    
    def LowerTriangular(self, expr, opts):
        pass

    def LowerUnitTriangular(self, expr, opts):
        pass
    
    def UpperTriangular(self, expr, opts):
        pass

    def UpperUnitTriangular(self, expr, opts):
        pass

    def Symmetric(self, expr, opts):
        pass

    def Matrix(self, expr, opts):
        pass

    def IdentityMatrix(self, expr, opts):
        pass

if __name__ == '__main__':
    pass
    import sigmacloog
#     sigmacloog.tosigma("/tmp/temp.scop", "/tmp/temp.sigma")
    s = sigmacloog.tosigma_str("/tmp/temp.scop")
    print s
#     Constraint.equality_from_aff(c.get_aff())
#                        reva = c.get_aff().mul(Aff.read_from_str(c.get_ctx(),"{[]->[(-1)]}"))
#                         revc = Constraint.equality_from_aff(reva)

#     s1 = Set("{[i,k]: 0<=i<4 and i<=k<4}")
#     s2 = Set("{[k,j]: 0<=k<4 and 0<=j<=k}")
#     c1 = s1.get_basic_sets()[0].get_constraints()
#     c2 = s2.get_basic_sets()[0].get_constraints()
# #     print c2[0].is_lower_bound(dim_type.set, 0)
# #     print c2[3].is_lower_bound(dim_type.set, 0)
# #     e0 = Constraint.equality_from_aff(c2[0].get_aff())
# #     e1 = Constraint.equality_from_aff(c2[3].get_aff())
#     import re
#     aff_re = re.compile("{ \[.*\] -> \[(.*)\] }")
#     ctx = Context()
#     args = [ aff_re.search(str(c1[2].set_coefficient_val(dim_type.set, 1, 0).get_aff().mul(Aff.read_from_str(ctx,"{[]->[(-1)]}")) )) ]
#     args.append( aff_re.search(str(c2[0].set_coefficient_val(dim_type.set, 0, 0).get_aff().mul(Aff.read_from_str(ctx,"{[]->[(-1)]}")) )) )
#     args.append( aff_re.search(str(c2[3].set_coefficient_val(dim_type.set, 0, 0).get_aff().mul(Aff.read_from_str(ctx,"{[]->[(-1)]}")) )) )
#     
#     maxs = "max(" + args[0].group(1) + ", " + args[1].group(1) + ")"
#     maxs = "max(" + maxs + ", " + args[2].group(1) + ")"
#     pwaff = PwAff.read_from_str(ctx, "{[i,j,k]->[(k - "+maxs+")]}")
#     pcs = pwaff.get_pieces()
# 
#     s = Set("{ [i, j, k] : 1=0 }")
#     for pc in pcs:
#         s = s.union( pc[0].add_constraint(Constraint.equality_from_aff(pc[1])) )
#     print s
#     print s.add_constraints([])
# #     print c1.get_aff().union_add(c2.get_aff())
# #     print Set("{[i,j,k]: 0<=i<4 and 0<=j<=k and k=max(max(0,i),j)}")
# #     print Set("{[i,j,k]: 0<=i<4 and 0<=j<=k and k=0}") == Set("{[i,j,k]: 0<=i<4 and 0<=j<=k and k=max(0,i)}") 
# #     print c1.set_coefficient_val(dim_type.set, 1, 0).get_aff()
# #     print c2.set_coefficient_val(dim_type.set, 0, 0).get_aff()
#         
# #     coeff = c.get_coefficient_val(dim_type.set, 1)
# #     print s2
