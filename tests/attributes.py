#!/usr/bin/python
# tests/attributes.py -- test interface for netlink message attributes
# Copyright 2011 Sean Robinson <seankrobinson@gmail.com>
#
# This file is part of the pymnl package, a Python interface
# for netlink sockets.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public License
#  as published by the Free Software Foundation; either version 2.1 of
#  the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA
#

from random import randint
import unittest

import pymnl
from pymnl.attributes import *

class TestAttributes(unittest.TestCase):

    def _test_integer_constructor(self, method_, max_value_):
        """ Test the specified integer constructor.

            method_ - Attr constructor to test

            max_value_ - maximum value the integer can hold
        """
        for type_ in (TYPE_U8, TYPE_U16, TYPE_U32, TYPE_U64):
            # valid values
            random_ = randint(1, max_value_ - 1)
            for value_ in (0, random_, max_value_):
                self.assertTrue(isinstance(method_(type_, value_), Attr),
                                        "test value did not make an Attr")
            # invalid values
            random_ = randint(-1 * (max_value_ - 1), -2)
            for value_ in (-1, random_, -1 * max_value_, "test string"):
                self.assertRaises(TypeError, method_, type_, value_)

    def _test_integer_length(self, method_, max_value_, aligned_len_):
        """ Test the specified integer length.

            method_ - Attr constructor to test

            max_value_ - maximum value the integer can hold

            aligned_len_ - length of Attr value aligned to NLA size (in
                bytes); this value should not include the attribute header
        """
        for type_ in (TYPE_U8, TYPE_U16, TYPE_U32, TYPE_U64):
            random_ = randint(1, max_value_ - 1)
            for value_ in (0, random_, max_value_):
                one_attr = method_(type_, value_)
                # valid values
                self.assertEqual(len(one_attr), ATTR_HDRLEN + aligned_len_,
                            "length does not match expected Attr length")
                # invalid values
                self.assertNotEqual(len(method_(type_, value_)),
                            ATTR_HDRLEN + randint(0, aligned_len_ - 1),
                            "length unexpectedly matches")

    def test_u8(self):
        """ Test new_u8() constructor and expected length.
        """
        max_value_ = pow(2, 8) - 1
        self._test_integer_constructor(Attr.new_u8, max_value_)
        self._test_integer_length(Attr.new_u8, max_value_, 4)

    def test_u16(self):
        """ Test new_u16() constructor and expected length.
        """
        max_value_ = pow(2, 16) - 1
        self._test_integer_constructor(Attr.new_u16, max_value_)
        self._test_integer_length(Attr.new_u16, max_value_, 4)

    def test_u32(self):
        """ Test new_u32() constructor and expected length.
        """
        max_value_ = pow(2, 32) - 1
        self._test_integer_constructor(Attr.new_u32, max_value_)
        self._test_integer_length(Attr.new_u32, max_value_, 4)

    def test_u64(self):
        """ Test new_u64() constructor and expected length.
        """
        max_value_ = pow(2, 64) - 1
        self._test_integer_constructor(Attr.new_u64, max_value_)
        self._test_integer_length(Attr.new_u64, max_value_, 8)

    def test_strnz(self):
        """ Test new_strnz() constructor and expected length.
        """
        for type_ in (TYPE_U8, TYPE_STRING):
            # valid values
            for test_string_ in ("test string", "nl80211", "spam"):
                aligned_len_ = NLA_ALIGN(len(test_string_))
                strnz_ = Attr.new_strnz(type_, test_string_)
                self.assertTrue(isinstance(strnz_, Attr),
                                        "test string did not make an Attr")
                self.assertEqual(len(strnz_), (ATTR_HDRLEN + aligned_len_),
                                        "test string is wrong length")
            # invalid values
            random_ints_ = []
            for i_ in range(3): random_ints_.append(randint(-1000, 1000))
            for value_ in (random_ints_):
                self.assertRaises(TypeError, Attr.new_strnz, type_, value_)

    def test_strz(self):
        """ Test new_strz() constructor and expected length.
        """
        for type_ in (TYPE_U8, TYPE_NUL_STRING):
            # valid values
            for test_string_ in ("test string", "nl80211", "spam"):
                aligned_len_ = NLA_ALIGN(len(test_string_) + 1)
                strz_ = Attr.new_strz(type_, test_string_)
                self.assertTrue(isinstance(strz_, Attr),
                                        "test string did not make an Attr")
                self.assertEqual(len(strz_), (ATTR_HDRLEN + aligned_len_),
                                        "test string is wrong length")
            # invalid values
            random_ints_ = []
            for i_ in range(3): random_ints_.append(randint(-1000, 1000))
            for value_ in (random_ints_):
                self.assertRaises(TypeError, Attr.new_strz, type_, value_)

    @staticmethod
    def suite():
        return unittest.TestLoader().loadTestsFromTestCase(TestAttributes)

