from SDLParser import *
from SDLang import *
#from toolbox.pairinggroup import pair
#"""
#A and B :- an array of group elements in G1 and G2 respectively
#a and b :- array of group elements in ZR
#"""
#def pairing_product(A, a, B, b):
#    assert len(A) == len(B), "arrays must be of equal length! Check size of 'A' or 'B'"
#    assert type(a) == dict and type(b) == dict, "exponent list should be of type 'dict'"
#    default_exp = 1
#    
#    for i in range(len(A)):
#        if a.get(i) == None: a[i] = default_exp
#        if b.get(i) == None: b[i] = default_exp
#    
#    prod_result = 1
#    for i in range(len(A)):
#        prod_result *= pair(A[i] ** a[i], B[i] ** b[i])
#    
#    return prod_result

class AbstractTechnique:
    def __init__(self, allStmtsInBlock):
        assert type(allStmtsInBlock) == dict, "Invalid dict of code block"
        self.allStmtsInBlock = allStmtsInBlock

    def visit(self, node, data):
        return
    # check whether left or right node is constant

    def getNodes(self, tree, parent_type, _list):
        if tree == None: return None
        elif parent_type == ops.MUL:
            if tree.type == ops.ATTR: _list.append(tree)
            elif tree.type == ops.EXP: _list.append(tree)
            elif tree.type == ops.HASH: _list.append(tree)
        
        if tree.left: self.getNodes(tree.left, tree.type, _list)
        if tree.right: self.getNodes(tree.right, tree.type, _list)
        return

    def getVarDef(self, name):
        if name in self.allStmtsInBlock.keys():
            # return the corresponding VarInfo object
            assert type(self.allStmtsInBlock[name]) == VarInfo, "not a valid varInfo object."
            return self.allStmtsInBlock[name]
        return None 

    @classmethod
    def getMulTokens(self, subtree, parent_type, target_type, _list):
        if subtree == None: return None
        elif parent_type == ops.MUL:
            if subtree.type in target_type: _list.append(subtree); return            
        if subtree.left: self.getMulTokens(subtree.left, subtree.type, target_type, _list)
        if subtree.right: self.getMulTokens(subtree.right, subtree.type, target_type, _list)
        return
    
    def isConstInSubtreeT(self, node):
        if Type(node) == ops.ATTR:
            return True
        return False
    
    @classmethod
    def addATTRToList(self, node, _list_dups, _list_unique):
        _list_dups.append(node)
        for i in _list_unique:
            if str(node) == str(i): return            
        _list_unique.append(node)
        return

    def findManyExpWithIndex(self, node, index, _list, _list2):
        node_type = Type(node)
        #print("node_type = ", node_type)
        if node == None: return None
        elif node_type == ops.EXP:
            # look for a^b_z or a^(b_z * s) where if z appears in right then return
            # the EXP right node as a acceptable candidate
            print("node.right type =>", Type(node.right))
            if Type(node.right) == ops.MUL:
                my_list = []
                self.getMulTokens(node.right, node_type, [ops.ATTR], my_list) # we are just interested in ATTR ndoes for this side
                for i in my_list:
                    if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: self.addATTRToList(i, _list, _list2) # _list.append(i)
                my_list2 = []
                self.getMulTokens(node.left, Type(node.left), [ops.EXP, ops.ATTR], my_list2) # interested in EXP and ATTR nodes here
#                print("should test left?: ", node.left, len(my_list2))
                for i in my_list2:
                    if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: _list.append(i) # standard x_z case
                    elif Type(i) == ops.EXP and not i.right.isAttrIndexEmpty() and index in i.right.attr_index: self.addATTRToList(i.right, _list, _list2) # handle a^x_z case
            
            if Type(node.left) == ops.MUL:
                print("JAA: in this case now.")
                my_list = []; my_list2 = []
                self.getMulTokens(node.left, node_type, [ops.EXP, ops.ATTR], my_list) # we are just interested in ATTR ndoes for this side
                for i in my_list:
                    print("i: ", i)
                    if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: _list.append(i)
                    elif Type(i) == ops.EXP and not i.right.isAttrIndexEmpty() and index in i.right.attr_index: self.addATTRToList(i.right, _list, _list2) # handle a^x_z case                    
                if Type(node.right) == ops.ATTR:
                    print("i2: ", node.right)
                    if not node.right.isAttrIndexEmpty() and index in node.right.attr_index: self.addATTRToList(node.right, _list, _list2)
                else:
                    self.getMulTokens(node.right, node_type, [ops.ATTR], my_list2) # interested in EXP and ATTR nodes here                    
                    for i in my_list2:
                        if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: self.addATTRToList(i, _list, _list2) # standard x_z case
                

        elif node_type == ops.MUL:
            my_list = []; my_list2 = []
            if Type(node.left) == ops.MUL:
                self.getMulTokens(node.left, ops.MUL, [ops.ATTR], my_list)
                #print("\t\tCONSIDER THIS CASE 1: ", len(my_list))
                for i in my_list:
                    if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: self.addATTRToList(i, _list, _list2)
            else:
                print("JAA: missing case: ", )
            
            if Type(node.right) == ops.MUL:
                self.getMulTokens(node.right, ops.MUL, [ops.ATTR], my_list2)
                print("\t\tCONSIDER THIS CASE 2: ", len(my_list2))
                for i in my_list2:
                    if Type(i) == ops.ATTR and not i.isAttrIndexEmpty() and index in i.attr_index: self.addATTRToList(i, _list, _list2)
                
        else:
            result = self.findManyExpWithIndex(node.left, index, _list)
            result = self.findManyExpWithIndex(node.right, index, _list)
            return
    
    @classmethod
    def findManyExpWithIndex2(self, node, index, _list, _list2):
        debug = False
        if node.left: self.findManyExpWithIndex2(node.left, index, _list, _list2)
        if node.right: self.findManyExpWithIndex2(node.right, index, _list, _list2)
        if debug: print("visiting child node: ", node)
        if Type(node) == ops.ATTR:
            if debug: print("does node matche? :=> ", node)
            if not node.isAttrIndexEmpty() and index in node.attr_index:
               if debug:  print("add this node: ", node)
               self.addATTRToList(node, _list, _list2)
        else:
            if debug: print("continue...", node)
            pass
        return

    def findExpWithIndex(self, node, index):
        node_type = Type(node)
        #print("node_type = ", node_type)
        if node == None: return None
        elif node_type == ops.EXP:
            # look for a^b_z or a^(b_z * s) where if z appears in right then return
            # the EXP right node as a acceptable candidate
            # debug: print("node.right type =>", Type(node.right))
            if Type(node.right) == ops.MUL:
                return self.findExpWithIndex(node.right, index)                
            elif not node.right.isAttrIndexEmpty() and index in node.right.attr_index:
                #print("node =>", node)            
                return node.right
        elif node_type == ops.MUL:
            if not node.left.isAttrIndexEmpty() and not node.right.isAttrIndexEmpty():
                if index in node.left.attr_index and index in node.right.attr_index: 
                    return node
            elif not node.left.isAttrIndexEmpty() and index in node.left.attr_index: return node.left
            elif not node.left.isAttrIndexEmpty() and index in node.right.attr_index: return node.right            
        else:
            result = self.findExpWithIndex(node.left, index)
            if result: return node
            result = self.findExpWithIndex(node.right, index)
            return result

    def isAttrIndexInNode(self, node, index):
        node_type = Type(node)
        #print("node_type = ", node_type)
        if node == None: return None
        elif node_type == ops.ATTR:
            #print("node.right type =>", Type(node.right))
            if str(node.attr) == "delta":
                pass
            elif node.attr_index and index in node.attr_index:
                return True
            return False
        else:
            result = self.isAttrIndexInNode(node.left, index)
            if result: return result
            result = self.isAttrIndexInNode(node.right, index)
            return result
    
    @classmethod
    def createPair2(self, left, right):
        pair = BinaryNode(ops.PAIR)
        pair.left = BinaryNode.copy(left)
        pair.right = BinaryNode.copy(right)
        return pair
        
    def createPair(self, left, right):
        pair = BinaryNode(ops.PAIR)
        pair.left = left
        pair.right = right
        return pair
    
    def createSplitPairings(self, left, right, list_nodes):        
        nodes = list_nodes;
        muls = [ BinaryNode(ops.MUL) for i in range(len(nodes)-1) ]
        if left.type == ops.MUL:
            for i in range(len(muls)):
                muls[i].left = self.createPair(nodes[i], BinaryNode.copy(right))
                if i < len(muls)-1:
                    muls[i].right = muls[i+1]
                else:
                    muls[i].right = self.createPair(nodes[i+1], BinaryNode.copy(right))
            return muls[0]
        elif right.type == ops.MUL:
            for i in range(len(muls)):
                muls[i].left = self.createPair(BinaryNode.copy(left), nodes[i])
                if i < len(muls)-1:
                    muls[i].right = muls[i+1]
                else:
                    muls[i].right = self.createPair(BinaryNode.copy(left), nodes[i+1])
            return muls[0]            
        return None
    
    @classmethod
    def createMul(self, left, right):
        if left.type == right.type and left.type == ops.EXP:
            # test whether exponents are the same
            l = str(left.right)
            r = str(right.right)
#            print(l, r)
            if l == r: # in other words, the same exponent
                mul = AbstractTechnique.createMul(left.left, right.left)
                exp = BinaryNode(ops.EXP, mul, BinaryNode.copy(left.right))
                return exp
            else:
                return BinaryNode(ops.MUL, left, right) # for now
        else:
            return BinaryNode(ops.MUL, BinaryNode.copy(left), BinaryNode.copy(right))
    
    @classmethod    
    def createInvExp(self, left):
        inv_node = BinaryNode("-1")
        new = BinaryNode.copy(left)
        if Type(new) == ops.EXP:
            if Type(new.right) == ops.ATTR:
                new.right.negated = not new.right.negated
            elif Type(new.right) == ops.MUL:
                # case 1: a^(b * c) transforms to a^(-b * -c)
                # case 2: a^((x + y) * b) transforms to a^((x + y) * -b) 
                subnodes = []
                getListNodes(new.right, ops.EXP, subnodes)
                if len(subnodes) > 0:
                    for i in subnodes: 
                        if Type(i) == ops.ATTR: i.negated = not i.negated
                else:
                    return self.createMul(new, inv_node)
#                print("Result: ", new)
                return new
            else: # ADD, DIV, SUB, etc
                print("warning: not tested yet in createInvExp():", Type(new), 
                      self.createMul(new, inv_node))
                return new
        elif Type(new) == ops.ON:
            new.right = self.createInvExp(new.right)
        else:
#            print("handle case 2.")
            return self.createExp(new, inv_node)
        return new
    
    def createMulFromList(self, _list):
        if len(_list) > 1:
            muls = [ BinaryNode(ops.MUL) for i in range(len(_list)-1) ]
            for i in range(len(muls)):
                muls[i].left = BinaryNode.copy(_list[i])
                if i < len(muls)-1: muls[i].right = muls[i+1]
                else: muls[i].right = BinaryNode.copy(_list[i+1])
            return muls[0] # MUL nodes absorb the exponent
        else:
            return BinaryNode.copy(_list[0]) # don't bother creating a MUL node for this

    @classmethod
    def negateThis(self, node):
        if Type(node) == ops.ATTR:
            node.negated = True
        if node.left: self.negateThis(node.left)
        if node.right: self.negateThis(node.right)
    
    # TODO: turn EXP and Pair into classmethods
    @classmethod
    def createExp(self, left, right):
        if left.type == ops.EXP: # left => a^b , then => a^(b * c)
#            exp = BinaryNode(ops.EXP)
            if Type(left.right) == ops.ATTR:
                value = left.right.getAttribute()
                if value.isdigit() and int(value) <= 1:  
#                    exp.left = left.left
                    if right.negated: 
#                        print("Before double negation: ", left, right)
                        left.right.negated = False; 
                        right.negated = False 
#                        print("After double negation: ", left, right)
                    else:                        
                    #left.right.setAttribute(str(right))
                        self.negateThis(right)
                    BinaryNode.setNodeAs(left.right, right)
                    #print("adjusted negation nodes: ", left.right)
# JAA commented out to avoid extra index, for example, 'delta_z_z' for VRF 
#                    print("original: ", left.right.attr_index)
#                    left.right.attr_index = right.attr_index                    
#                    print("post: ", left.right.attr_index)
                    mul = left.right
                else:
                    mul = BinaryNode(ops.MUL)
                    mul.left = left.right
                    mul.right = right                    
            else:
                mul = BinaryNode(ops.MUL)
                mul.left = left.right
                mul.right = right
            exp = BinaryNode(ops.EXP)
            exp.left = left.left
            exp.right = mul                
        elif left.type in [ops.ATTR, ops.PAIR, ops.HASH]: # left: attr ^ right
            exp = BinaryNode(ops.EXP)
            exp.left = left
            exp.right = right
        elif left.type == ops.MUL:
            nodes = []
            self.getMulTokens(left, ops.NONE, [ops.EXP, ops.PAIR, ops.HASH, ops.ATTR], nodes)
            #getListNodes(left, ops.NONE, nodes)
#            print("createExp sub nodes:")
#            for i in nodes:
#                print("subnodes: ", i)
            if len(nodes) > 2: # only distribute exponent when there are 
                muls = [ BinaryNode(ops.MUL) for i in range(len(nodes)-1) ]
                for i in range(len(muls)):
                    muls[i].left = self.createExp(nodes[i], BinaryNode.copy(right))
                    if i < len(muls)-1: muls[i].right = muls[i+1]
                    else: muls[i].right = self.createExp(nodes[i+1], BinaryNode.copy(right))
                exp = muls[0] # MUL nodes absorb the exponent
            else:
                exp = BinaryNode(ops.EXP)
                exp.left = left
                exp.right = right
        else:
            exp = BinaryNode(ops.EXP)
            exp.left = left
            exp.right = right
        return exp

    @classmethod
    def createExp2(self, left, right, _listIFMul=None):
        if left.type == ops.EXP: # left => a^b , then => a^(b * c)
#            exp = BinaryNode(ops.EXP)
            if Type(left.right) == ops.ATTR:
                value = left.right.getAttribute()
                if value.isdigit() and int(value) <= 1:  
#                    exp.left = left.left                   
#                    print("mul : ", str(right), left.right) 
                    if right.negated: 
                        print("Set negation here 2!")
                        left.right.negated = False; 
                        right.negated = False 
                    else:
                        self.negateThis(right)
                        
                    left.right.setAttribute(str(right)) 
#                    left.right.attr_index = right.attr_index
                    mul = left.right
                elif "1" in right.getAttribute():
#                    print("WORD: ", right)
                    mul = left.right
                    if mul.negated and right.negated: mul.negated = True
                    else: mul.negated = right.negated
                else:
                    mul = BinaryNode(ops.MUL)
                    mul.left = left.right
                    mul.right = right                    
            else:
                mul = BinaryNode(ops.MUL)
                mul.left = left.right
                mul.right = right
            exp = BinaryNode(ops.EXP)
            exp.left = left.left
            exp.right = mul                
        elif left.type in [ops.ATTR, ops.PAIR, ops.HASH]: # left: attr ^ right
            exp = BinaryNode(ops.EXP)
            exp.left = left
            exp.right = right
        elif left.type == ops.MUL:
            nodes = []
            if not _listIFMul: _listIFMul = [ops.EXP, ops.HASH, ops.ATTR]
            self.getMulTokens(left, ops.MUL, _listIFMul, nodes)
#            getListNodes(left, ops.EQ_TST, nodes)
#            print("createExp sub nodes:")
#            for i in nodes:
#                print("subnodes: ", i)
            if len(nodes) >= 2: # only distribute exponent when there are 
                muls = [ BinaryNode(ops.MUL) for i in range(len(nodes)-1) ]
                for i in range(len(muls)):
                    muls[i].left = self.createExp2(nodes[i], BinaryNode.copy(right), _listIFMul)
                    if i < len(muls)-1: muls[i].right = muls[i+1]
                    else: muls[i].right = self.createExp2(nodes[i+1], BinaryNode.copy(right), _listIFMul)
                exp = muls[0] # MUL nodes absorb the exponent
            else:
                exp = BinaryNode(ops.EXP)
                exp.left = left
                exp.right = right
        else:
            exp = BinaryNode(ops.EXP)
            exp.left = left
            exp.right = right
        return exp

    
    # node - target subtree, parent - self-explanatory
    # target - node we would liek to delete, branch - side of tree that is traversed.
    def deleteFromTree(self, node, parent, target, branch=None):
        if node == None: return None
        elif str(node) == str(target):
            if branch == side.left: 
                BinaryNode.setNodeAs(parent, parent.right)
                parent.left = parent.right = None 
                return                
            elif branch == side.right: 
                BinaryNode.setNodeAs(parent, parent.left)
                parent.left = parent.right = None
                return
        else:
            self.deleteFromTree(node.left, node, target, side.left)
            self.deleteFromTree(node.right, node, target, side.right)

    def deleteNodesFromTree(self, node, parent, targets, branch=None):
        if node.left: self.deleteNodesFromTree(node.left, node, targets, side.left)
        if node.right: self.deleteNodesFromTree(node.right, node, targets, side.right)
        if self.debug: print("visiting child node: ", node)
        if node.left == None and node.right == None:
            if self.debug: print(node, " in target? ", node in targets)
            if node in targets:
               if self.debug:  print("delete myself: ", node) # delete myself 
               BinaryNode.clearNode(node)
        elif Type(node.left) != ops.NONE and Type(node.right) == ops.NONE: 
            if self.debug: print("left is there and right NOT there! action: delete right and move up left")
            BinaryNode.setNodeAs(node, node.left)
        elif Type(node.left) == ops.NONE and Type(node.right) != ops.NONE:
            if self.debug: print("left is NOT there and right is there. action: delete left and move up right")
            BinaryNode.setNodeAs(node, node.right)
        elif Type(node.left) == ops.NONE and Type(node.right) == ops.NONE:
            if self.debug: print("left is NOT there and right is NOT there. action: delete root node and move on")
            BinaryNode.clearNode(node)
        elif Type(node.left) != ops.NONE and Type(node.right) != ops.NONE:
            if self.debug: print("left and right BOTH there. action: do nothing and continue")
            pass
        else:
            if self.debug: print("continue...", node)
            pass

Tech_db = Enum('NoneApplied', 'ExpIntoPairing', 'DistributeExpToPairing', 'SplitPairing', 'DivIntoMul')
# Rule: 'e(g, h)^d_i' transform into ==> 'e(g^d_i, h)' iff g or h is constant == (attribute node)
# move exponent towards the non-constant attribute
class Technique1(AbstractTechnique):
    def __init__(self, allStmtsInBlock):
        AbstractTechnique.__init__(self, allStmtsInBlock)
        self.rule    = "Move the exponent(s) into the pairing (technique 2)"
        self.applied = False 
        self.score   = Tech_db.NoneApplied
        self.debug   = False
    
    # find: 'e(g, h)^d_i' transform into ==> 'e(g^d_i, h)' iff g or h is constant == (attribute node)
    # move exponent towards the non-constant attribute
    def visit_exp(self, node, data):
        #print("left node =>", node.left.type,"target right node =>", node.right)
        if(Type(node.left) == ops.PAIR):   # and (node.right.attr_index == 'i'): # (node.right.getAttribute() == 'delta'):
            pair_node = node.left
                                  # make cur node the left child of pair node
            # G1 : pair.left, G2 : pair.right
            left_check = not self.isConstInSubtreeT(pair_node.left)
            right_check = not self.isConstInSubtreeT(pair_node.right)
            if self.debug: print("T2: visit_exp => left check:", left_check, ", right check:", right_check)
            if left_check == right_check and left_check == False:
                #print("T2: handle this case :=>", pair_node)
                # move to first by default since both are constant!
                addAsChildNodeToParent(data, pair_node) # move pair node one level up
                pair_node.left = self.createExp(pair_node.left, node.right)
                self.applied = True
                self.score   = Tech_db.ExpIntoPairing                
            elif left_check:
                addAsChildNodeToParent(data, pair_node) # move pair node one level up
                pair_node.left = self.createExp(pair_node.left, node.right)
                #print("pair_node :", pair_node.left)
#               node.left = pair_node.left
#               pair_node.left = node                
                self.applied = True
                self.score   = Tech_db.ExpIntoPairing
                #print("T2: Left := Move '" + str(node.right) + "' exponent into the pairing.")
            
            elif right_check:       
                addAsChildNodeToParent(data, pair_node) # move pair node one level up                
                pair_node.right = self.createExp(pair_node.right, node.right)
#                node.left = pair_node.right
#                pair_node.right = node 
                self.applied = True                
                self.score   = Tech_db.ExpIntoPairing                
                #print("T2: Right := Move '" + str(node.right) + "' exponent into the pairing.")
            else:
                print("T2: Need to consider other cases here: ", pair_node)
                return
        # blindly move the right node of prod{} on x^delta regardless    
        elif(Type(node.left) == ops.ON):
            # (prod{} on x) ^ y => prod{} on x^y
            # check whether prod right
            prod_node = node.left
            prod_node.right = self.createExp2(prod_node.right, BinaryNode.copy(node.right))
            print("New prod node: ", prod_node)
            addAsChildNodeToParent(data, prod_node)
            print("exponent moving towards right: ", prod_node.right)
            if Type(prod_node.right) == ops.MUL:
                print("T2: dot prod with pair: ", prod_node)
                print("MUL on right: ", prod_node.right)
                _subnodes = []
                getListNodes(prod_node.right, ops.NONE, _subnodes)
                if len(_subnodes) > 2:
                            # basically call createExp to distribute the exponent to each
                            # MUL node in pair_node.right
                    new_mul_node = self.createExp(prod_node.right, node.right)
                    prod_node.right = new_mul_node
                    self.applied = True
                    self.score   = Tech_db.DistributeExpToPairing
#                            print("new pair node: ", pair_node, "\n")                            
                            #self.rule += "distributed exponent into the pairing: right side. "
                else:
                    self.setNodeAs(prod_node, side.right, node, side.left)
                    self.applied = True       
                    self.score   = Tech_db.ExpIntoPairing                   
                            #self.rule += "moved exponent into the pairing: less than 2 mul nodes. "

            elif Type(prod_node.right) in [ops.HASH, ops.ATTR]:
                print("T2 - exercise pair_node : right = ATTR : ", prod_node.right)
                        # set pair node left child to node left since we've determined
                        # that the left side of pair node is not a constant
                self.setNodeAs(prod_node, side.right, node, side.left)
                self.applied = True
                self.score   = Tech_db.ExpIntoPairing
            else:
                pass
# COMMENT OUT FOR NOW
#            elif Type(prod_node.right) == ops.EXP:
#                pass
#            else:
#                print("Else case: ", prod_node.right, Type(prod_node.right), "\n")
#                #    blindly make the exp node the right child of whatever node
#                self.setNodeAs(prod_node, side.right, node, side.left)
#                self.applied = True
#                self.score   = Tech_db.ExpIntoPairing
                
        elif(Type(node.left) == ops.MUL):    
            # distributing exponent over a MUL node (which may have more MUL nodes)        
            #print("Consider: node.left.type =>", node.left.type)                
            mul_node = node.left
            if self.debug: 
                print("distribute exp correctly =>")
                print("left: ", mul_node.left)
                print("right: ", mul_node.right, Type(mul_node.right))
            if Type(data['parent']) != ops.PAIR: 
                pass
                mul_node.left = self.createExp(mul_node.left, BinaryNode.copy(node.right))
                mul_node.right = self.createExp(mul_node.right, BinaryNode.copy(node.right))
#                print("result for right: ", mul_node.right, "\n\n")
                addAsChildNodeToParent(data, mul_node)
                self.applied = True
                self.score   = Tech_db.DistributeExpToPairing
            #else:
            #    print("something went wrong!")
            #self.rule += " distributed the exp node when applied to a MUL node. "
            # Note: if the operands of the mul are ATTR or PAIR doesn't matter. If the operands are PAIR nodes, PAIR ^ node.right
            # This is OK b/c of preorder visitation, we will apply transformations to the children once we return.
            # The EXP node of the mul children nodes will be visited, so we can apply technique 2 for that node.
        elif(Type(node.left) == ops.ATTR):
#            print("Need to add logic for this: ", node.left, node.right)
            if str(node.right) != "-1": return
            assign = self.getVarDef(str(node.left))
            if assign: 
                var_node = assign.getAssignNode() # EQ node
                if Type(var_node) == ops.EQ: 
                    new_node = self.createExp2(var_node.right, node.right)
                    var_node.right = new_node
                    addAsChildNodeToParent(data, node.left)
                    print("Move exponent inside: ", var_node)
        else:
            #print("Other cases not ATTR?: ", Type(node.left))
            return
    
    # A quick way to reassign node pointers
    # 1. sets orig_node (left or right side) to target_node
    # 2. sets target_node (left or right side) to orig_node's specified side
    def setNodeAs(self, orig_node, attr_str, target_node, target_attr_str=side.left):
        if attr_str == side.right:  tmp_node = orig_node.right; orig_node.right = target_node
        elif attr_str == side.left: tmp_node = orig_node.left; orig_node.left = target_node
        else: return None
        if target_attr_str == side.left: target_node.left = tmp_node
        elif target_attr_str == side.right: target_node.right = tmp_node
        else: return None
        return True


# Rule 2: transform x / y to x * y^-1 if y is ATTR or PAIR node
class Technique2(AbstractTechnique):
    def __init__(self, allStmtsInBlock):
        AbstractTechnique.__init__(self, allStmtsInBlock)
        self.rule    = "Transform division operation into multiplication to inverse (technique 2)"
        self.applied = False 
        self.score   = Tech_db.NoneApplied
        self.debug   = False

    def visit_div(self, node, data):
        if Type(node.right) in [ops.PAIR, ops.ATTR]:
            new_exp_node = self.createInvExp(node.right)
            node.right = new_exp_node
            node.setType(ops.MUL)
            self.applied = True
            self.score   = Tech_db.DivIntoMul

# Rule 3: transform e(a, b*c*d) => e(a, b) * e(a, c) * e(a, d) OR
# e(a*b*c, d) => e(a, d) * e(b, d) * e(c, d)
class Technique3(AbstractTechnique):
    def __init__(self, allStmtsInBlock):
        AbstractTechnique.__init__(self, allStmtsInBlock)
        self.rule    = "Split pairings in all cases (technique 3)"
        self.applied = False 
        self.score   = Tech_db.NoneApplied
        self.debug   = False
    
    def visit_pair(self, node, data):            
        l = []; r = [];
        self.getMulTokens(node.left, ops.NONE, [ops.EXP, ops.HASH, ops.ATTR], l)
        self.getMulTokens(node.right, ops.NONE, [ops.EXP, ops.HASH, ops.ATTR], r)
        if self.debug:
            print("T3: visit_on left list: ")
            for i in l: print(i)
            print("right list: ")
            for i in r: print(i)
            
        if len(l) >= 2 and len(r) <= 1: 
            right = node.right # right side of pairing is the constant
            new_pair_nodes = self.createSplitPairings(node.left, right, l)
            self.applied = True
            self.score   = Tech_db.SplitPairing
            addAsChildNodeToParent(data, new_pair_nodes)                
            # Note the same check does not apply to the left side b/c we want to move as many operations
            # into the smallest group G1. Therefore, if there are indeed more than two MUL nodes on the left side
            # of pairing, then that's actually a great thing and will give us the most savings.
        elif len(r) >= 2 and len(l) <= 1:
                # special case: reverse split a \single\ pairing into two or more pairings to allow for application of 
                # other techniques. pair(a, b * c * d?) => p(a, b) * p(a, c) * p(a, d)
                # pair with a child node with more than two mult's?
            left = node.left # left side of pairing is the constant
            new_pair_nodes = self.createSplitPairings(left, node.right, r)
            self.applied = True
            self.score   = Tech_db.SplitPairing
            addAsChildNodeToParent(data, new_pair_nodes)
        else:
            if self.debug:
                print("len l: ", len(l))
                print("len r: ", len(r))
            pass # do nothing

# Formerly 'DotProdInstanceFinder' from AutoBatch
# Focuses on simplifying dot products of the form
# prod{} on (x * y)
class Technique4(AbstractTechnique):
    def __init__(self, allStmtsInBlock):
        AbstractTechnique.__init__(self, allStmtsInBlock)
        self.rule = "Distribute dot products (technique 5): "
        self.applied = False

    def getMulTokens(self, subtree, parent_type, target_type, _list):
        if subtree == None: return None
        elif parent_type == ops.EXP and Type(subtree) == ops.MUL:
            return               
        elif parent_type == ops.MUL:
            if Type(subtree) in target_type: 
                found = False
                for i in _list:
                    if isNodeInSubtree(i, subtree): found = True
                if not found: _list.append(subtree)

        if subtree.left: self.getMulTokens(subtree.left, subtree.type, target_type, _list)
        if subtree.right: self.getMulTokens(subtree.right, subtree.type, target_type, _list)
        return
        
    def visit(self, node, data):
        pass

    def visit_pair(self, node, data):
        return { 'visited_pair': True }
    
    # Bandaid: cleaning up when about to distribute a dot products where PROD node has no ON node
    # in other words, dangling PROD node in verify equation
    def visit_prod(self, node, data):
        if Type(data['parent']) != ops.ON:
            #print("Found a candidate for cleaning!!!")
            new_node = BinaryNode(ops.ATTR)
            new_node.setAttribute("1")
            BinaryNode.clearNode(node)
            BinaryNode.setNodeAs(node, new_node)
            
            
    # visit all the ON nodes and test whether we can distribute the product to children nodes
    # e.g., prod{} on (x * y) => prod{} on x * prod{} on y    
    def visit_on(self, node, data):
#        print("DP finder: ", data.get('visited_pair'))
        if Type(data['parent']) == ops.PAIR or data.get('visited_pair'): # bail if dot prod already a child of a pairing node
            return
        #print("T5: right node type =>", Type(node.right), node.right)
        if Type(node.right) == ops.ON: # prod{} on (prod{} on x). thus, we should bail
            return
        #print("test: right node of prod =>", node.right, ": type =>", node.right.type)
        #print("parent type =>", Type(data['parent']))
#        _type = node.right.type
        if Type(node.right) == ops.MUL:            
            # must distribute prod to both children of mul
            r = []
            mul_node = node.right
            self.getMulTokens(mul_node, ops.NONE, [ops.EXP, ops.HASH, ops.PAIR, ops.ATTR], r)
            #for i in r:
            #    print("node =>", i)
            
            if len(r) == 0:
                pass
            elif len(r) <= 2:
            # in case we're dealing with prod{} on attr1 * attr2 
            # no need to simply further, so we can simply return
                if mul_node.left.type == ops.ATTR and mul_node.right.type == ops.ATTR:
                    return

                node.right = None
                prod_node2 = BinaryNode.copy(node)
            
            # add prod nodes to children of mul_node
                prod_node2.right = mul_node.right
                mul_node.right = prod_node2
            
                node.right = mul_node.left
                mul_node.left = node
                #self.rule += "True "
                # move mul_node one level up to replace the "on" node.
                addAsChildNodeToParent(data, mul_node) # from SDLParser
                self.applied = True
            elif len(r) > 2:
                #print("original node =>", node)
                muls = [BinaryNode(ops.MUL) for i in range(len(r)-1)]
                prod = [BinaryNode.copy(node) for i in r]
                # distribute the products to all nodes in r
                for i in range(len(r)):
                    prod[i].right = r[i]
#                    print("n =>", prod[i])
                # combine prod nodes into mul nodes                     
                for i in range(len(muls)):
                    muls[i].left = prod[i]
                    if i < len(muls)-1:
                        muls[i].right = muls[i+1]
                    else:
                        muls[i].right = prod[i+1]
#                print("final node =>", muls[0])
                addAsChildNodeToParent(data, muls[0]) # from SDLParser
                self.applied = True
                #self.rule += "True "
            else:
                #self.rule += "False "
                return                
    def testForApplication(self):
        return self.applied


class Technique11(AbstractTechnique):
    def __init__(self, allStmtsInBlock, varTypes={}):
        AbstractTechnique.__init__(self, allStmtsInBlock)
        self.varTypes = varTypes
        self.rule    = "Unroll constant-size dot product (technique 10)"
        self.applied = False 
#        self.score   = tech10.NoneApplied
        self.debug = False      
        self.loopStmt   = None
        self.prod_start = None
        self.prod_end = None
        self.prod_iterator = None

    def visit_on(self, node, data):
        if Type(node.left) == ops.PROD:
            self.loopStmt = node.right

    def visit_prod(self, node, data):
        if(Type(node.left) == ops.EQ):
            start = node.left
            self.prod_iterator = start.left.getAttribute()
            self.prod_start = int(start.right.getAttribute())
            if self.prod_start == None or self.prod_iterator == None: sys.exit("ERROR: for loop not well formed!") 
            print("prod: ", self.prod_iterator, ":", self.prod_start)                       
        if(Type(node.right) == ops.ATTR):
            val = node.right.getAttribute()
            if val.isdigit():
                self.prod_end = int(val)
            elif self.varTypes.get(val):
                # if the val is actually a variable, then need to find var definition in sdl
                self.prod_end = int(self.varTypes.get(val)) # abstract class call
            else:
                self.prod_end = None
                
            if self.prod_end == None: sys.exit("ERROR: %s is not defined in SDL." % val)
            print("until: ", node.right, self.prod_end)
    
    def testForApplication(self):
        if self.prod_start != None and self.prod_iterator != None and self.prod_end != None:
            self.applied = True
#            self.score   = tech10.ConstantSizeLoop
        else:
            self.applied = False
        return self.applied

#    def varDefineValue(self, var_name):
#        var = self.vars.get(str(var_name))
#        return var


# performs step 1 from above. Replaces 't' (target variables) with integer values in each attribute
class EvaluateAtIntValue:
    def __init__(self, target_var, int_value):
        self.target_var = target_var
        self.int_value  = int_value
        self.debug      = False
    
    def visit(self, node, data):
        pass
   
    def visit_attr(self, node, data):#    
        attr = node.getAttribute()
        new_attr = ''
        s = attr.split('#') 
        if( len(s) > 1 ):
            if self.debug: print("attr: ", node, s)
            for i in s:
                if i == self.target_var:
                    new_attr += str(self.int_value)
                elif self.target_var in i: # instead of t+1 or t-1 or etc replace with the evaluated result                    
                    exec("%s = %s" % (self.target_var, self.int_value))
                    new_attr += str(eval(i))
                else:
                    new_attr += i
                new_attr += '#'
            new_attr = new_attr[:-1] # cut off last character
            if self.debug: print("new_attr: ", new_attr)
            node.setAttribute(new_attr)

def applyTechnique11(equation, code_block={}):
#    sdl_data = {'N':10} # example input?
    Tech11 = Technique11( code_block )
    ASTVisitor(Tech11).preorder(equation)
    
    if Tech11.testForApplication():
        dot_prod_list = []
        evalint = EvaluateAtIntValue(Tech11.prod_iterator, Tech11.prod_start)
        testEq = BinaryNode.copy(Tech11.loopStmt)
        ASTVisitor(evalint).preorder(testEq)
        dot_prod_list.append(testEq)
#        print("Evaluated version at %d: %s" % (Tech10.prod_start, testEq))
#        print("Combine the rest into this one...")
        for t in range(Tech11.prod_start+1, Tech11.prod_end):
            evalint = EvaluateAtIntValue(Tech11.prod_iterator, t)  
            testEq2 = BinaryNode.copy(Tech11.loopStmt)
            ASTVisitor(evalint).preorder(testEq2)
#            print("Eval-n-Combine version at %d: %s" % (t, testEq2))
            dot_prod_list.append(testEq2)
        testEqCombined = Tech11.createMulFromList( dot_prod_list )
        print("Result: ", testEqCombined)
        return testEqCombined
    return None

class FindT1:
    def __init__(self, T0_var):
        self.T0 = T0_var
        self.T1 = None
        self.decout_op = None
        
    def visit(self, node, data):
        if Type(node.left) == ops.ATTR:
            var_name = node.left.getFullAttribute()
            print("Visiting this node :=", node, self.T0)
            if var_name == self.T0:
                self.T1 = node.right
                self.decout_op = Type(node)
                print("T1 right :=", self.T1)
#                self.T1 = data['sibling']
        elif Type(node.right) == ops.ATTR:
            var_name = node.right.getFullAttribute()
            if var_name == self.T0:
                self.T1 = node.left
                self.decout_op = Type(node)
                print("T1 left :=", self.T1)

class SubstituteVar:
    def __init__(self, target, new_var):
        self.target = target
        self.new_var = new_var
    def visit(self, node, data):
        pass
    
    def visit_attr(self, node, data):
        if str(node) == self.target:
            node.setAttribute(self.new_var)

    def visit_list(self, node, data):
        found = False
        if node.listNodes != None:
            for i in node.listNodes:
                if str(i) == self.target: found = True; break
        if found:
            ind = node.listNodes.index(self.target)
            node.listNodes[ind] = self.new_var

class SubstitutePairings:
    def __init__(self, this, this_new, side='left'):
        self.this_target = this
        self.this_new    = this_new
        self.side        = side
    def visit(self, node, data):
        pass
    
    def visit_pair(self, node, data):
        # TODO: may not be ATTR nodes: look for other cases
        if self.side == 'left' and str(node.left) == self.this_target and Type(node.left) == ops.ATTR:
            if self.this_new != None: node.left.setAttribute(self.this_new)
        elif self.side == 'right' and str(node.right) == self.this_target and Type(node.right) == ops.ATTR:
            if self.this_new != None: node.right.setAttribute(self.this_new)
        else:
            print("TODO: handle this case - ", Type(node.left), Type(node.right))

techMap = {1:Technique1, 2:Technique2, 3:Technique3, 4:Technique4, 11:Technique11}

def testTechnique(tech_option, equation, code_block=None):
    if code_block == None: code_block = {} 
    eq2 = BinaryNode.copy(equation)
        
    tech = None
    if tech_option in techMap.keys():
        tech = techMap[tech_option](code_block)
    else:
        return None
        
    # traverse equation with the specified technique
    ASTVisitor(tech).preorder(eq2)

    # return the results
    return (tech, eq2)

# figures out which optimizations apply
def SimplifySDLNode(equation, path, code_block=None, debug=False):
    tech_list = [1, 2, 3] # 4
    # 1. apply the start technique to equation
    new_eq = equation
    while True:
        cur_tech = tech_list.pop()
        if debug: print("Testing technique: ", cur_tech)
        (tech, new_eq) = testTechnique(cur_tech, new_eq, code_block)
        
        if tech.applied:
            if debug: print("Technique ", cur_tech, " successfully applied.")
            path.append(cur_tech)
            tech_list = [1, 2, 3]
            continue
        else:
            if len(tech_list) == 0: break
    if debug: 
        print("path: ", path)
        print("optimized equation: ", new_eq)
    return new_eq

if __name__ == "__main__":
    statement = sys.argv[1]
    parser = SDLParser()
    equation = parser.parse(statement)
    
    path_applied = []
    
    print("Original: ", equation)
    equation2 = SimplifySDLNode(equation, path_applied)
    print("Final Optimized: ", equation2)
    print("Techniques: ", path_applied)
    applyTechnique11(equation2)
#    tech2 = Technique2({})
#    ASTVisitor(tech2).preorder(equation)
#    print("Tech 2: ", equation)
#        
#    tech1 = Technique1({})
#    ASTVisitor(tech1).preorder(equation)
#    print("Tech 1: ", equation)
#    
#    tech3 = Technique3({})
#    ASTVisitor(tech3).preorder(equation)
#    print("Tech 3: ", equation)
#    
#    tech4 = Technique4({})
#    ASTVisitor(tech4).preorder(equation)
#    print("Tech 4: ", equation)
    
    
    