import os
import json
from common import update_json_file, get_logger, exec_cmd
from yamlparser import Parser
from pathlib import Path

logger = get_logger("update-image")


# Functions that work to update gluu_versions.json

def determine_final_official_and_dev_version(tag_list):
    """
    Determine official version i.e 4.1.0 , 4.2.2..etc using oxauths repo
    @param tag_list:
    @return:
    """
    # Check for the highest major.minor.patch i.e 4.2.0 vs 4.2.2
    dev_image = ""
    patch_list = []
    for tag in tag_list:
        patch_list.append(int(tag[4:5]))
    # Remove duplicates
    patch_list = list(set(patch_list))
    # Sort
    patch_list.sort()
    highest_major_minor_patch_number = str(patch_list[-1])
    versions_list = []
    for tag in tag_list:
        if "dev" in tag and tag[4:5] == highest_major_minor_patch_number:
            dev_image = tag[0:5] + "_dev"
        # Exclude any tag with the following
        if "dev" not in tag and "a" not in tag and tag[4:5] == highest_major_minor_patch_number:
            versions_list.append(int(tag[6:8]))
    # A case were only a dev version of a new patch is available then a lower stable patch should be checked.
    # i.e there is no 4.5.0_01 but there is 4.5.1_dev
    if not versions_list:
        highest_major_minor_patch_number = str(int(highest_major_minor_patch_number) - 1)
        for tag in tag_list:
            if not dev_image and "dev" in tag and tag[4:5] == highest_major_minor_patch_number:
                dev_image = tag[0:5] + "_dev"
            # Exclude any tag with the following
            if "dev" not in tag and "a" not in tag and tag[4:5] == highest_major_minor_patch_number:
                versions_list.append(int(tag[6:8]))

    # Remove duplicates
    versions_list = list(set(versions_list))
    # Sort
    versions_list.sort()
    # Return highest patch
    highest_major_minor_patch_image_patch = str(versions_list[-1])
    if len(highest_major_minor_patch_image_patch) == 1:
        highest_major_minor_patch_image_patch = "0" + highest_major_minor_patch_image_patch

    highest_major_minor_patch_image = ""
    for tag in tag_list:
        if "dev" not in tag and highest_major_minor_patch_image_patch in tag \
                and tag[4:5] == highest_major_minor_patch_number:
            highest_major_minor_patch_image = tag

    return highest_major_minor_patch_image, dev_image


def determine_major_version(all_repos_tags):
    """
    Determine official major version i.e 4.1 , 4.2..etc using oxauths repo
    @param all_repos_tags:
    @return:
    """
    versions_list = []
    for tag in all_repos_tags["oxauth"]:
        # Exclude any tag with the following
        if "dev" not in tag \
                and "latest" not in tag \
                and "secret" not in tag \
                and "gluu-engine" not in tag:
            versions_list.append(float(tag[0:3]))
    # Remove duplicates
    versions_list = list(set(versions_list))
    # Sort
    versions_list.sort()
    # Return highest version
    return versions_list[-1]


def get_docker_repo_tag(org, repo):
    """
    Returns a dictionary of all available tags for a certain repo
    :param org:
    :param repo:
    :return:
    """
    logger.info("Getting docker tag for repository {}.".format(repo))
    exec_get_repo_tag_curl_command = ["curl", "-s",
                                      "https://hub.docker.com/v2/repositories/{}/{}/tags/?page_size=100".format(org,
                                                                                                                repo)]
    stdout, stderr, retcode = None, None, None
    try:
        stdout, stderr, retcode = exec_cmd(" ".join(exec_get_repo_tag_curl_command))

    except (IndexError, Exception):
        manual_curl_command = " ".join(exec_get_repo_tag_curl_command)
        logger.error("Failed to curl\n{}".format(manual_curl_command))
    all_tags = json.loads(stdout)["results"]
    image_tags = []
    for tag in all_tags:
        image_tags.append(tag["name"])
    image_tags_dict = dict()
    image_tags_dict[repo] = image_tags
    return image_tags_dict


def filter_all_repo_dictionary_tags(all_repos_tags, major_official_version):
    """
    Analyze the dictionary containing all repos and keeps only the  list of tags and versions matching the major version
    @param all_repos_tags:
    @param major_official_version:
    """
    filtered_all_repos_tags = dict()

    for repo, tag_list in all_repos_tags.items():
        temp_filtered_tag_list = []
        for tag in tag_list:
            if major_official_version == tag[0:3]:
                temp_filtered_tag_list.append(tag)
        filtered_all_repos_tags[repo] = temp_filtered_tag_list
    return filtered_all_repos_tags


def analyze_filtered_dict_return_final_dict(filtered_all_repos_tags, major_official_version):
    """
    Analyze filtered dictionary and return the final dict with only one official version and one dev version
    @param filtered_all_repos_tags:
    @param major_official_version:
    """
    final_official_version_dict = dict()
    final_dev_version_dict = dict()
    # Gluus main values.yaml
    gluu_values_file = Path("../pygluu/kubernetes/templates/helm/gluu/values.yaml").resolve()
    gluu_values_file_parser = Parser(gluu_values_file, True)
    dev_version = ""

    def update_dicts_and_yamls(name, rep, tags_list, helm_name=None):
        final_tag, final_dev_tag = determine_final_official_and_dev_version(tags_list)
        final_official_version_dict[name + "_IMAGE_NAME"] = "gluufederation/" + rep
        final_dev_version_dict[name + "_IMAGE_NAME"] = "gluufederation/" + rep
        final_official_version_dict[name + "_IMAGE_TAG"], final_dev_version_dict[name + "_IMAGE_TAG"] \
            = final_tag, final_dev_tag
        if rep != "upgrade":
            if helm_name:
                gluu_values_file_parser[helm_name]["image"]["repository"] = "gluufederation/" + rep
                gluu_values_file_parser[helm_name]["image"]["tag"] = final_tag
            else:
                gluu_values_file_parser[rep]["image"]["repository"] = "gluufederation/" + rep
                gluu_values_file_parser[rep]["image"]["tag"] = final_tag

    for repo, tag_list in filtered_all_repos_tags.items():
        official_version, dev_version = determine_final_official_and_dev_version(tag_list)
        if repo == "casa":
            update_dicts_and_yamls("CASA", repo, tag_list)
        elif repo == "oxd-server":
            update_dicts_and_yamls("OXD", repo, tag_list)
        elif repo == "fido2":
            update_dicts_and_yamls("FIDO2", repo, tag_list)
        elif repo == "scim":
            update_dicts_and_yamls("SCIM", repo, tag_list)
        elif repo == "config-init":
            update_dicts_and_yamls("CONFIG", repo, tag_list, "config")
        elif repo == "cr-rotate":
            update_dicts_and_yamls("CACHE_REFRESH_ROTATE", repo, tag_list)
        elif repo == "certmanager":
            update_dicts_and_yamls("CERT_MANAGER", repo, tag_list, "oxauth-key-rotation")
        elif repo == "opendj":
            update_dicts_and_yamls("LDAP", repo, tag_list, "opendj")
        elif repo == "jackrabbit":
            update_dicts_and_yamls("JACKRABBIT", repo, tag_list)
        elif repo == "oxauth":
            update_dicts_and_yamls("OXAUTH", repo, tag_list)
        elif repo == "oxpassport":
            update_dicts_and_yamls("OXPASSPORT", repo, tag_list)
        elif repo == "oxshibboleth":
            update_dicts_and_yamls("OXSHIBBOLETH", repo, tag_list)
        elif repo == "oxtrust":
            update_dicts_and_yamls("OXTRUST", repo, tag_list)
        elif repo == "persistence":
            update_dicts_and_yamls("PERSISTENCE", repo, tag_list)
        elif repo == "upgrade":
            update_dicts_and_yamls("UPGRADE", repo, tag_list)
    gluu_versions_dict = {major_official_version: final_official_version_dict,
                          dev_version: final_dev_version_dict}
    gluu_values_file_parser.dump_it()
    return gluu_versions_dict


def main():
    all_repos_tags = dict()
    org = os.environ.get("ORG_NAME", "gluufederation")
    gluu_docker_repositories_names_used_in_cn = ["casa", "fido2", "scim", "config-init",
                                                 "cr-rotate", "certmanager", "opendj", "jackrabbit", "oxauth",
                                                 "oxd-server", "oxpassport", "oxshibboleth",
                                                 "oxtrust", "persistence", "upgrade"]

    for repo in gluu_docker_repositories_names_used_in_cn:
        all_repos_tags.update(get_docker_repo_tag(org, repo))

    major_official_version = str(determine_major_version(all_repos_tags))

    filtered_all_repos_tags = filter_all_repo_dictionary_tags(all_repos_tags, major_official_version)
    final_gluu_versions_dict = analyze_filtered_dict_return_final_dict(filtered_all_repos_tags, major_official_version)
    update_json_file(final_gluu_versions_dict, '../pygluu/kubernetes/templates/gluu_versions.json')


if __name__ == '__main__':
    main()
