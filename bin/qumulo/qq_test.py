#!/usr/bin/env python
# Copyright (c) 2015 Qumulo, Inc. All rights reserved.
#
# NOTICE: All information and intellectual property contained herein is the
# confidential property of Qumulo, Inc. Reproduction or dissemination of the
# information or intellectual property contained herein is strictly forbidden,
# unless separate prior written permission has been obtained from Qumulo, Inc.

import qpaths
qpaths.setpaths()

import os
import subprocess
import unittest

import qinternal.check.pycheck as pycheck
import qinternal.core.posix_fs as posix_fs

class PublicQQCommandsMixin(object):
    def test_ad_cancel_help(self):
        self.do_help_test('ad_cancel')

    def test_ad_join_help(self):
        self.do_help_test('ad_join')

    def test_ad_leave_help(self):
        self.do_help_test('ad_leave')

    def test_ad_list_help(self):
        self.do_help_test('ad_list')

    def test_ad_poll_help(self):
        self.do_help_test('ad_poll')

    def test_add_nodes_help(self):
        self.do_help_test('add_nodes')

    def test_auth_add_group_help(self):
        self.do_help_test('auth_add_group')

    def test_auth_add_user_help(self):
        self.do_help_test('auth_add_user')

    def test_auth_delete_group_help(self):
        self.do_help_test('auth_delete_group')

    def test_auth_delete_user_help(self):
        self.do_help_test('auth_delete_user')

    def test_auth_list_group_help(self):
        self.do_help_test('auth_list_group')

    def test_auth_list_groups_help(self):
        self.do_help_test('auth_list_groups')

    def test_auth_list_user_help(self):
        self.do_help_test('auth_list_user')

    def test_auth_list_users_help(self):
        self.do_help_test('auth_list_users')

    def test_auth_mod_group_help(self):
        self.do_help_test('auth_mod_group')

    def test_auth_mod_user_help(self):
        self.do_help_test('auth_mod_user')

    def test_auth_set_password_help(self):
        self.do_help_test('auth_set_password')

    def test_change_password_help(self):
        self.do_help_test('change_password')

    def test_cluster_conf_help(self):
        self.do_help_test('cluster_conf')

    def test_cluster_config_get_help(self):
        self.do_help_test('cluster_config_get')

    def test_cluster_slots_help(self):
        self.do_help_test('cluster_slots')

    def test_disks_status_get_help(self):
        self.do_help_test('disks_status_get')

    def test_dns_resolve_ips_help(self):
        self.do_help_test('dns_resolve_ips')

    def test_floating_ip_allocation_help(self):
        self.do_help_test('floating_ip_allocation')

    def test_fs_create_dir_help(self):
        self.do_help_test('fs_create_dir')

    def test_fs_create_file_help(self):
        self.do_help_test('fs_create_file')

    def test_fs_create_link_help(self):
        self.do_help_test('fs_create_link')

    def test_fs_create_symlink_help(self):
        self.do_help_test('fs_create_symlink')

    def test_fs_delete_help(self):
        self.do_help_test('fs_delete')

    def test_fs_delete_tree_help(self):
        self.do_help_test('fs_delete_tree')

    def test_fs_file_get_attr_help(self):
        self.do_help_test('fs_file_get_attr')

    def test_fs_file_samples_help(self):
        self.do_help_test('fs_file_samples')

    def test_fs_file_set_attr_help(self):
        self.do_help_test('fs_file_set_attr')

    def test_fs_get_acl_help(self):
        self.do_help_test('fs_get_acl')

    def test_fs_get_stats_help(self):
        self.do_help_test('fs_get_stats')

    def test_fs_read_help(self):
        self.do_help_test('fs_read')

    def test_fs_read_dir_help(self):
        self.do_help_test('fs_read_dir')

    def test_fs_read_dir_aggregates_help(self):
        self.do_help_test('fs_read_dir_aggregates')

    def test_fs_rename_help(self):
        self.do_help_test('fs_rename')

    def test_fs_resolve_paths_help(self):
        self.do_help_test('fs_resolve_paths')

    def test_fs_set_acl_help(self):
        self.do_help_test('fs_set_acl')

    def test_fs_walk_tree_help(self):
        self.do_help_test('fs_walk_tree')

    def test_fs_write_help(self):
        self.do_help_test('fs_write')

    def test_get_vpn_keys_help(self):
        self.do_help_test('get_vpn_keys')

    def test_halt_help(self):
        self.do_help_test('halt')

    def test_halt_cluster_help(self):
        self.do_help_test('halt_cluster')

    def test_install_vpn_keys_help(self):
        self.do_help_test('install_vpn_keys')

    def test_iops_get_help(self):
        self.do_help_test('iops_get')

    def test_login_help(self):
        self.do_help_test('login')

    def test_logout_help(self):
        self.do_help_test('logout')

    def test_monitoring_conf_help(self):
        self.do_help_test('monitoring_conf')

    def test_network_conf_get_help(self):
        self.do_help_test('network_conf_get')

    def test_network_conf_mod_help(self):
        self.do_help_test('network_conf_mod')

    def test_network_poll_help(self):
        self.do_help_test('network_poll')

    def test_nfs_add_share_help(self):
        self.do_help_test('nfs_add_share')

    def test_nfs_delete_share_help(self):
        self.do_help_test('nfs_delete_share')

    def test_nfs_list_share_help(self):
        self.do_help_test('nfs_list_share')

    def test_nfs_list_shares_help(self):
        self.do_help_test('nfs_list_shares')

    def test_nfs_mod_share_help(self):
        self.do_help_test('nfs_mod_share')

    def test_node_state_get_help(self):
        self.do_help_test('node_state_get')

    def test_nodes_list_help(self):
        self.do_help_test('nodes_list')

    def test_restart_help(self):
        self.do_help_test('restart')

    def test_restart_cluster_help(self):
        self.do_help_test('restart_cluster')

    def test_restriper_status_help(self):
        self.do_help_test('restriper_status')

    def test_set_cluster_conf_help(self):
        self.do_help_test('set_cluster_conf')

    def test_set_monitoring_conf_help(self):
        self.do_help_test('set_monitoring_conf')

    def test_smb_add_share_help(self):
        self.do_help_test('smb_add_share')

    def test_smb_delete_share_help(self):
        self.do_help_test('smb_delete_share')

    def test_smb_list_share_help(self):
        self.do_help_test('smb_list_share')

    def test_smb_list_shares_help(self):
        self.do_help_test('smb_list_shares')

    def test_smb_mod_share_help(self):
        self.do_help_test('smb_mod_share')

    def test_static_ip_allocation_help(self):
        self.do_help_test('static_ip_allocation')

    def test_system_config_get_help(self):
        self.do_help_test('system_config_get')

    def test_time_get_help(self):
        self.do_help_test('time_get')

    def test_time_series_get_help(self):
        self.do_help_test('time_series_get')

    def test_time_set_help(self):
        self.do_help_test('time_set')

    def test_time_status_help(self):
        self.do_help_test('time_status')

    def test_unconfigured_help(self):
        self.do_help_test('unconfigured')

    def test_unconfigured_nodes_list_help(self):
        self.do_help_test('unconfigured_nodes_list')

    def test_upgrade_config_help(self):
        self.do_help_test('upgrade_config')

    def test_upgrade_config_set_help(self):
        self.do_help_test('upgrade_config_set')

    def test_upgrade_status_help(self):
        self.do_help_test('upgrade_status')

    def test_version_help(self):
        self.do_help_test('version')

    def test_who_am_i_help(self):
        self.do_help_test('who_am_i')

class QQTest(unittest.TestCase, PublicQQCommandsMixin):
    '''
    QQTest creates a sandbox environment that tries to simulate running QQ
    without the Qumulo src environment, and shows that it still works.

    Ideally, this would be a virtualenv with a pip install of the newly-built
    qumulo_rest_client python package.
    '''
    def setUp(self):
        cli_fs = copy_path('cli')
        self.qq_fs = posix_fs.ChrootFileSystem(cli_fs.translate('cli'))

    def do_help_test(self, subcommand):
        returncode, stdout, stderr = \
            run_cmd(self.qq_fs, 'qq', subcommand, '--help')
        self.assertEqual((returncode, stderr), (0, ''))
        self.assertIn(' '.join(['usage:', 'qq', subcommand, '[-h]']), stdout)

def copy_file(dst_fs, src_fs, filename):
    dst_fs.put(filename, src_fs.contents(filename))
    dst_fs.chmod(filename, src_fs.stat(filename).st_mode)

def copy_path(dir_, dst_fs=None):
    '''
    Copies files from the src directory to some dst_fs.
    '''
    src_fs = posix_fs.SrcFileSystem()
    dst_fs = posix_fs.TestFileSystem() if dst_fs is None else dst_fs

    copied = False
    for dirpath, _dirnames, filenames in src_fs.walk(dir_):
        dst_fs.makedirs(dirpath)

        filenames = [os.path.join(dirpath, f) for f in filenames
                     if not f.endswith('test.py')]
        for filename in filenames:
            copy_file(dst_fs, src_fs, filename)
            copied = True

    if not copied:
        copy_file(dst_fs, src_fs, dir_)

    return dst_fs

BASE_PATH = ['/usr/bin', '/usr/sbin', '/sbin', '/bin']

def run_cmd(fs, *args):
    '''
    Runs a command with the given FS root in the PATH (and little else.)
    '''
    output_fs = posix_fs.TestFileSystem()
    env = {}
    env['HOME'] = output_fs.translate('.')
    env['PATH'] = ':'.join(BASE_PATH + [fs.translate('.')])
    with open(output_fs.translate('stdout'), 'w') as stdout, \
         open(output_fs.translate('stderr'), 'w') as stderr:
        returncode = subprocess.call(list(args), stdout=stdout, stderr=stderr,
            cwd=output_fs.translate('.'), env=env)

    return (returncode,
            output_fs.contents('stdout'),
            output_fs.contents('stderr'))

if __name__ == '__main__':
    pycheck.main()
