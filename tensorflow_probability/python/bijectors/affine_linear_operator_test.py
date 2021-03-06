# Copyright 2018 The TensorFlow Probability Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""AffineLinearOperator Tests."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Dependency imports
import numpy as np
import tensorflow as tf
from tensorflow_probability.python import bijectors as tfb


class AffineLinearOperatorTest(tf.test.TestCase):

  def testIdentity(self):
    with self.test_session():
      affine = tfb.AffineLinearOperator(validate_args=True)
      x = np.array([[1, 0, -1], [2, 3, 4]], dtype=np.float32)
      y = x
      ildj = 0.

      self.assertEqual(affine.name, "affine_linear_operator")
      self.assertAllClose(y, affine.forward(x).eval())
      self.assertAllClose(x, affine.inverse(y).eval())
      self.assertAllClose(ildj, affine.inverse_log_det_jacobian(
          y, event_ndims=2).eval())
      self.assertAllClose(
          -affine.inverse_log_det_jacobian(y, event_ndims=2).eval(),
          affine.forward_log_det_jacobian(x, event_ndims=2).eval())

  def testDiag(self):
    with self.test_session():
      shift = np.array([-1, 0, 1], dtype=np.float32)
      diag = np.array([[1, 2, 3],
                       [2, 5, 6]], dtype=np.float32)
      scale = tf.linalg.LinearOperatorDiag(diag, is_non_singular=True)
      affine = tfb.AffineLinearOperator(
          shift=shift, scale=scale, validate_args=True)

      x = np.array([[1, 0, -1], [2, 3, 4]], dtype=np.float32)
      y = diag * x + shift
      ildj = -np.sum(np.log(np.abs(diag)), axis=-1)

      self.assertEqual(affine.name, "affine_linear_operator")
      self.assertAllClose(y, affine.forward(x).eval())
      self.assertAllClose(x, affine.inverse(y).eval())
      self.assertAllClose(
          ildj, affine.inverse_log_det_jacobian(y, event_ndims=1).eval())
      self.assertAllClose(
          -affine.inverse_log_det_jacobian(y, event_ndims=1).eval(),
          affine.forward_log_det_jacobian(x, event_ndims=1).eval())

  def testTriL(self):
    with self.test_session():
      shift = np.array([-1, 0, 1], dtype=np.float32)
      tril = np.array([[[3, 0, 0],
                        [2, -1, 0],
                        [3, 2, 1]],
                       [[2, 0, 0],
                        [3, -2, 0],
                        [4, 3, 2]]],
                      dtype=np.float32)
      scale = tf.linalg.LinearOperatorLowerTriangular(
          tril, is_non_singular=True)
      affine = tfb.AffineLinearOperator(
          shift=shift, scale=scale, validate_args=True)

      x = np.array([[[1, 0, -1],
                     [2, 3, 4]],
                    [[4, 1, -7],
                     [6, 9, 8]]],
                   dtype=np.float32)
      # If we made the bijector do x*A+b then this would be simplified to:
      # y = np.matmul(x, tril) + shift.
      y = np.squeeze(np.matmul(tril, np.expand_dims(x, -1)), -1) + shift
      ildj = -np.sum(np.log(np.abs(np.diagonal(
          tril, axis1=-2, axis2=-1))))

      self.assertEqual(affine.name, "affine_linear_operator")
      self.assertAllClose(y, affine.forward(x).eval())
      self.assertAllClose(x, affine.inverse(y).eval())
      self.assertAllClose(
          ildj, affine.inverse_log_det_jacobian(
              y, event_ndims=2).eval())
      self.assertAllClose(
          -affine.inverse_log_det_jacobian(y, event_ndims=2).eval(),
          affine.forward_log_det_jacobian(x, event_ndims=2).eval())


if __name__ == "__main__":
  tf.test.main()
