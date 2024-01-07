# DO NOT EDIT this file. It is set up in such a way that if you make any edits,
# the test cases may change resulting in a broken local autograder.

# Imports
import numpy as np
import torch
import torch.nn as nn
import sys, os, pdb
from test import Test

# Append paths and run
sys.path.append("mytorch")
from gru_cell import *
from loss import *
from linear import *

sys.path.append("models")
import char_predictor

# DO NOT CHANGE -->
EPS = 1e-20
SEED = 2022

# -->


############################################################################################
################################   Section 3 - GRU    ######################################
############################################################################################


class GRUToyTest(Test):
    def __init__(self):
        pass

    def gru_cell_forward(self, cur_input, idx):
        # Get cur inputs
        input_dim = cur_input[0]
        hidden_dim = cur_input[1]
        seq_len = cur_input[2]
        np.random.seed(SEED)
        torch.manual_seed(SEED)
        # data = np.array([1, 1]).reshape((seq_len, input_dim))
        # hidden = np.array([-1, 1, 0]).reshape(hidden_dim)
        data = np.random.randint(low=-1, high=1, size=(seq_len, input_dim))
        hidden = np.random.randint(low=-1, high=1, size=hidden_dim)

        print('input data: {}'.format(data))
        print('hidden: {}'.format(hidden))

        # Make pytorch rnn cell and get weights
        pytorch_gru_cell = nn.GRUCell(input_dim, hidden_dim)
        state_dict = pytorch_gru_cell.state_dict()
        W_ih, W_hh = state_dict["weight_ih"].numpy(), state_dict["weight_hh"].numpy()
        b_ih, b_hh = state_dict["bias_ih"].numpy(), state_dict["bias_hh"].numpy()

        Wrx, Wzx, Wnx = np.split(W_ih, 3, axis=0)
        Wrh, Wzh, Wnh = np.split(W_hh, 3, axis=0)

        brx, bzx, bnx = np.split(b_ih, 3, axis=0)
        brh, bzh, bnh = np.split(b_hh, 3, axis=0)

        # PyTorch
        pytorch_result = (
            pytorch_gru_cell(
                torch.FloatTensor(data[idx].reshape(1, -1)),
                torch.FloatTensor(hidden.reshape(1, -1)),
            )
                .detach()
                .numpy()
                .squeeze(0)
        )

        # user
        user_gru_cell = GRUCell(input_dim, hidden_dim)
        user_gru_cell.init_weights(
            Wrx, Wzx, Wnx, Wrh, Wzh, Wnh, brx, bzx, bnx, brh, bzh, bnh
        )
        user_result = user_gru_cell.forward(data[idx], hidden)

        print('*** expected h_t: {}'.format(pytorch_result))
        print('*** got result: {}'.format(user_result))

        if not self.assertions(user_result, pytorch_result, "type", "h_t"):
            return False
        if not self.assertions(user_result, pytorch_result, "shape", "h_t"):
            return False
        if not self.assertions(user_result, pytorch_result, "closeness", "h_t"):
            return False

        return True

    def test_gru_forward_one_input(self):
        np.random.seed(SEED)
        torch.manual_seed(SEED)
        inputs = [[2, 3, 1]]
        idx = [0]  # index by the seq_len
        n = len(inputs)
        for i in range(n):
            print('\n*** time step {} ***'.format(i))
            cur_input = inputs[i]
            result = self.gru_cell_forward(cur_input, idx[i])
            if result != True:
                print("Failed GRU Forward Test: %d / %d" % (i + 1, n))
                return False
            else:
                print("*** passed ***")

        # Use to save test data for next semester
        # np.save(os.path.join('autograder', 'hw3_autograder',
        #                      'data', 'gru_forward.npy'), results, allow_pickle=True)

        return True

    def test_gru_forward_three_input(self):
        np.random.seed(SEED)
        torch.manual_seed(SEED)
        inputs = [[2, 3, 1], [2, 3, 1], [2, 3, 1]]
        idx = [0, 0, 0]  # index by the seq_len
        n = len(inputs)
        for i in range(n):
            print('\n*** time step {} ***'.format(i))
            cur_input = inputs[i]
            result = self.gru_cell_forward(cur_input, idx[i])
            if result != True:
                print("Failed GRU Forward Test: %d / %d" % (i + 1, n))
                return False
            else:
                print("*** passed ***")

        # Use to save test data for next semester
        # np.save(os.path.join('autograder', 'hw3_autograder',
        #                      'data', 'gru_forward.npy'), results, allow_pickle=True)

        return True

    def gru_cell_backward(self, idx):
        np.random.seed(SEED)
        torch.manual_seed(SEED)
        input_dim = 2
        hidden_dim = 3
        seq_len = 1

        batch_size = 1
        output_dim = 2

        # Foward Pass -------------------------->
        # data = np.array([1, 1]).reshape((seq_len, input_dim))
        # target = np.random.randint(0, output_dim, (batch_size,))
        # hidden = np.array([-1, 1, 0]).reshape(hidden_dim)

        data = np.random.randint(low=-1, high=1, size=(seq_len, input_dim))
        target = np.random.randint(0, output_dim, (batch_size,))
        hidden = np.random.randint(low=-1, high=1, size=hidden_dim)

        print('data: {}'.format(data))
        print(target)
        print('hidden: {}'.format(hidden))

        # Make pytorch rnn cell and get weights
        pytorch_gru_cell = nn.GRUCell(input_dim, hidden_dim)
        pytorch_gru_output = nn.Linear(hidden_dim, output_dim)

        state_dict = pytorch_gru_cell.state_dict()
        W_ih, W_hh = state_dict["weight_ih"].numpy(), state_dict["weight_hh"].numpy()
        b_ih, b_hh = state_dict["bias_ih"].numpy(), state_dict["bias_hh"].numpy()

        output_state_dict = pytorch_gru_output.state_dict()
        W, b = output_state_dict["weight"].numpy(), output_state_dict["bias"].numpy().reshape(-1,1)

        Wrx, Wzx, Wnx = np.split(W_ih, 3, axis=0)
        Wrh, Wzh, Wnh = np.split(W_hh, 3, axis=0)

        brx, bzx, bnx = np.split(b_ih, 3, axis=0)
        brh, bzh, bnh = np.split(b_hh, 3, axis=0)

        # Foward Pass -------------------------->
        # PyTorch
        py_input = nn.Parameter(torch.FloatTensor(data[idx]), requires_grad=True)
        py_hidden = nn.Parameter(torch.FloatTensor(hidden), requires_grad=True)

        pytorch_result = pytorch_gru_cell(
            py_input.reshape(1, -1), py_hidden.reshape(1, -1)
        )

        pytorch_result_np = (
            pytorch_gru_cell(py_input.reshape(1, -1), py_hidden.reshape(1, -1))
                .detach()
                .numpy()
                .squeeze()
        )

        # user
        print("*** forward pass ***")
        user_gru_cell = GRUCell(input_dim, hidden_dim)
        user_output_layer = Linear(hidden_dim, output_dim)
        user_gru_cell.init_weights(
            Wrx, Wzx, Wnx, Wrh, Wzh, Wnh, brx, bzx, bnx, brh, bzh, bnh
        )
        user_result = user_gru_cell.forward(data[idx], hidden)

        if not self.assertions(user_result, pytorch_result_np, "type", "h_t"):
            return False
        if not self.assertions(user_result, pytorch_result_np, "shape", "h_t"):
            return False
        if not self.assertions(user_result, pytorch_result_np, "closeness", "h_t"):
            return False
        print("*** passed ***")
        # <--------------------------------------

        # Backward pass -------------------------->
        # PyTorch
        pytorch_output = pytorch_gru_output(pytorch_result)
        criterion = nn.CrossEntropyLoss()
        loss = criterion(pytorch_output, torch.LongTensor(target))
        loss.backward()

        py_dx = py_input.grad.detach().numpy()
        py_dh = py_hidden.grad.detach().numpy()

        # user
        print("*** backward pass ***")
        user_output_layer.W = W
        user_output_layer.b = b
        user_output = user_output_layer.forward(user_result.reshape(-1, 1).T)

        my_criterion = SoftmaxCrossEntropy()
        my_labels_onehot = np.zeros((batch_size, output_dim))
        my_labels_onehot[np.arange(batch_size), target] = 1.0
        my_loss = my_criterion.forward(user_output.reshape(1, -1), my_labels_onehot).mean()

        delta = my_criterion.backward()
        #user_output_layer.x.reshape(1, -1)
        delta = user_output_layer.backward(delta)
        my_dx, my_dh = user_gru_cell.backward(delta)

        my_dx = my_dx.squeeze(0)
        my_dh = my_dh.squeeze(0)

        print('\t*** test dx_t ***')
        if not self.assertions(my_dx, py_dx, "type", "dx_t"):
            return False
        if not self.assertions(my_dx, py_dx, "shape", "dx_t"):
            return False
        if not self.assertions(my_dx, py_dx, "closeness", "dx_t"):
            return False
        print('\t*** passed ***')

        print('\t*** test dh_t')
        if not self.assertions(my_dh, py_dh, "type", "dh_t"):
            return False
        if not self.assertions(my_dh, py_dh, "shape", "dh_t"):
            return False
        if not self.assertions(my_dh, py_dh, "closeness", "dh_t"):
            return False
        print('\t*** passed ***')

        # dWs
        print('\t*** test dWs ***')
        dWrx = pytorch_gru_cell.weight_ih.grad[:hidden_dim]
        dWzx = pytorch_gru_cell.weight_ih.grad[hidden_dim: hidden_dim * 2]
        dWnx = pytorch_gru_cell.weight_ih.grad[hidden_dim * 2: hidden_dim * 3]

        dWrh = pytorch_gru_cell.weight_hh.grad[:hidden_dim]
        dWzh = pytorch_gru_cell.weight_hh.grad[hidden_dim: hidden_dim * 2]
        dWnh = pytorch_gru_cell.weight_hh.grad[hidden_dim * 2: hidden_dim * 3]

        if not self.assertions(user_gru_cell.dWrx, dWrx, "closeness", "dWrx"):
            return False
        if not self.assertions(user_gru_cell.dWzx, dWzx, "closeness", "dWzx"):
            return False
        if not self.assertions(user_gru_cell.dWnx, dWnx, "closeness", "dWnx"):
            return False
        if not self.assertions(user_gru_cell.dWrh, dWrh, "closeness", "dWrh"):
            return False
        if not self.assertions(user_gru_cell.dWzh, dWzh, "closeness", "dWzh"):
            return False
        if not self.assertions(user_gru_cell.dWnh, dWnh, "closeness", "dWnh"):
            return False
        print('\t*** passed ***')

        # dbs
        print('\t*** test dbs ***')
        dbrx = pytorch_gru_cell.bias_ih.grad[:hidden_dim]
        dbzx = pytorch_gru_cell.bias_ih.grad[hidden_dim: hidden_dim * 2]
        dbnx = pytorch_gru_cell.bias_ih.grad[hidden_dim * 2: hidden_dim * 3]

        dbrh = pytorch_gru_cell.bias_hh.grad[:hidden_dim]
        dbzh = pytorch_gru_cell.bias_hh.grad[hidden_dim: hidden_dim * 2]
        dbnh = pytorch_gru_cell.bias_hh.grad[hidden_dim * 2: hidden_dim * 3]

        if not self.assertions(user_gru_cell.dbrx, dbrx, "closeness", "dbir"):
            return False
        if not self.assertions(user_gru_cell.dbzx, dbzx, "closeness", "dbiz"):
            return False
        if not self.assertions(user_gru_cell.dbnx, dbnx, "closeness", "dbin"):
            return False
        if not self.assertions(user_gru_cell.dbrh, dbrh, "closeness", "dbhr"):
            return False
        if not self.assertions(user_gru_cell.dbzh, dbzh, "closeness", "dbhz"):
            return False
        if not self.assertions(user_gru_cell.dbnh, dbnh, "closeness", "dbhn"):
            return False
        print('\t*** passed ***')
        # <--------------------------------------
        print('*** passed ***')
        return True

    def test_gru_backward(self):
        # Test derivatives
        idx = [0]  # index by the seq_len
        n = len(idx)
        for i in range(n):
            result = self.gru_cell_backward(idx[i])
            if result != True:
                print("Failed GRU Backward Test: %d / %d" % (i + 1, n))
                return False
            else:
                print("Passed GRU Backward Test: %d / %d" % (i + 1, n))

        # Use to save test data for next semester
        # np.save(os.path.join('autograder', 'hw3_autograder',
        #                      'data', 'gru_backward.npy'), results, allow_pickle=True)

        return True

    def generate(self, mu, sigma, FEATURE_DIM):
        # np.random.seed(SEED)

        return sigma * np.random.randn(1, FEATURE_DIM) + mu

    def create_input_data(self, SEQUENCE, FEATURE_DIM):
        mean_a = [1.0] * FEATURE_DIM
        mean_b = [5.0] * FEATURE_DIM
        mean_c = [10.0] * FEATURE_DIM

        mean = {"a": mean_a, "b": mean_b, "c": mean_c}

        sigma = 0.2

        inputs = []

        for char in SEQUENCE:
            v = self.generate(np.array(mean[char]), sigma, FEATURE_DIM)
            inputs.append(v)

        inputs = np.vstack(inputs)
        return inputs

    def run_test(self):
        # Test forward
        self.print_name("Section 3.1 - GRU Forward")
        forward_outcome = self.test_gru_forward_one_input()
        self.print_outcome("GRU Forward", forward_outcome)
        if forward_outcome == False:
            self.print_failure("GRU Forward")
            return False

        forward_outcome = self.test_gru_forward_three_input()
        self.print_outcome("GRU Forward", forward_outcome)
        if forward_outcome == False:
            self.print_failure("GRU Forward")
            return False

        # Test Backward
        self.print_name("Section 3.2 - GRU Backward")
        backward_outcome = self.test_gru_backward()
        self.print_outcome("GRU backward", backward_outcome)
        if backward_outcome == False:
            self.print_failure("GRU Backward")
            return False

        return True
