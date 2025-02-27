/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
 * Copyright (C) 2022 ScyllaDB
 *
 * Modified by ScyllaDB
 */
package com.datastax.oss.driver.api.testinfra.ccm;

import com.datastax.oss.driver.api.core.Version;

/** @see CcmRule */
@SuppressWarnings("unused")
public class DefaultCcmBridgeBuilderCustomizer {

  public static CcmBridge.Builder configureBuilder(CcmBridge.Builder builder) {
    if (!CcmBridge.DSE_ENABLEMENT
        && CcmBridge.VERSION.nextStable().compareTo(Version.V4_0_0) >= 0) {
      if (CcmBridge.VERSION.nextStable().compareTo(Version.V4_1_0) >= 0) {
        builder.withCassandraConfiguration("materialized_views_enabled", true);
        builder.withCassandraConfiguration("sasi_indexes_enabled", true);
      } else {
        builder.withCassandraConfiguration("enable_materialized_views", true);
        builder.withCassandraConfiguration("enable_sasi_indexes", true);
      }
    }
    if (CcmBridge.VERSION.nextStable().compareTo(Version.V3_0_0) >= 0) {
      if (!CcmBridge.SCYLLA_ENABLEMENT) {
        // @IntegrationTestDisabledScyllaJVMArgs
        // FIXME: Add Scylla equivalents of those configuration options
        builder.withJvmArgs("-Dcassandra.superuser_setup_delay_ms=0");
        builder.withJvmArgs("-Dcassandra.skip_wait_for_gossip_to_settle=0");
      }
      builder.withCassandraConfiguration("num_tokens", "1");
      builder.withCassandraConfiguration("initial_token", "0");
    }
    return builder;
  }
}
